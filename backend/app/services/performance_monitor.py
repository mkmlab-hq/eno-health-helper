"""
통합 성능 모니터링 및 자동 최적화 서비스

핵심 기능:
- 실시간 성능 메트릭 수집 (응답 시간, 정확도, 처리량)
- 성능 병목 지점 자동 식별 (지연 시간, 정확도 저하, 처리량 저하)
- 동적 리소스 할당 (CPU 우선순위, CPU affinity, OOM 점수)
- 성능 이력 추적 및 트렌드 분석 (선형 추세)
- 자동 성능 최적화 제안 및 선택적 적용

사용 예시:

    from app.services.performance_monitor import PerformanceMonitor

    monitor = PerformanceMonitor()

    @monitor.instrument_operation(service_name="fusion", operation_name="analyze")
    def analyze(data):
        # ... 작업 수행 ...
        return {"accuracy": 0.92, "result": "ok"}

    # 또는 컨텍스트 매니저 사용
    with monitor.monitor_span("fusion", "preprocess") as span:
        # ... 작업 ...
        span.set_accuracy(0.88)

    # 주기적 스냅샷/제안 조회
    snapshot = monitor.get_metrics_snapshot()
    suggestions = monitor.get_optimization_suggestions()

주의:
- psutil이 설치되어 있으면 보다 정교한 리소스 제어가 가능합니다. 미설치 시 일부 제어는 무시됩니다.
"""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import threading
import time
from collections import deque, defaultdict
from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None  # type: ignore

logger = logging.getLogger(__name__)


# ------------------------------
# 데이터 모델
# ------------------------------

@dataclass
class MetricEvent:
    service_name: str
    operation_name: str
    timestamp_ms: float
    latency_ms: float
    success: bool
    accuracy: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationStats:
    count: int
    success_ratio: float
    latency_avg_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput_per_min: float
    accuracy_avg: Optional[float]
    accuracy_min: Optional[float]


# ------------------------------
# 유틸: 롤링 윈도우 버퍼
# ------------------------------

class RollingWindowBuffer:
    def __init__(self, window_seconds: int = 300) -> None:
        self.window_ms = max(1, int(window_seconds * 1000))
        self._events: Deque[MetricEvent] = deque()
        self._lock = threading.Lock()

    def add_event(self, event: MetricEvent) -> None:
        with self._lock:
            self._events.append(event)
            self._prune_locked(now_ms=event.timestamp_ms)

    def _prune_locked(self, now_ms: Optional[float] = None) -> None:
        if now_ms is None:
            now_ms = time.time() * 1000.0
        cutoff = now_ms - self.window_ms
        while self._events and self._events[0].timestamp_ms < cutoff:
            self._events.popleft()

    def snapshot(self) -> List[MetricEvent]:
        with self._lock:
            self._prune_locked()
            return list(self._events)

    def compute_stats(self) -> Optional[OperationStats]:
        events = self.snapshot()
        if not events:
            return None

        latencies = sorted([e.latency_ms for e in events])
        count = len(events)
        successes = sum(1 for e in events if e.success)
        success_ratio = successes / count if count else 0.0

        def percentile(sorted_values: List[float], p: float) -> float:
            if not sorted_values:
                return 0.0
            k = (len(sorted_values) - 1) * p
            f = int(k)
            c = min(f + 1, len(sorted_values) - 1)
            if f == c:
                return sorted_values[int(k)]
            d0 = sorted_values[f] * (c - k)
            d1 = sorted_values[c] * (k - f)
            return d0 + d1

        latency_avg = mean(latencies)
        p50 = percentile(latencies, 0.50)
        p95 = percentile(latencies, 0.95)
        p99 = percentile(latencies, 0.99)

        # throughput per minute = count in window / window_minutes
        window_minutes = max(1e-6, self.window_ms / 60000.0)
        throughput_per_min = count / window_minutes

        accuracies = [e.accuracy for e in events if e.accuracy is not None]
        accuracy_avg = mean(accuracies) if accuracies else None
        accuracy_min = min(accuracies) if accuracies else None

        return OperationStats(
            count=count,
            success_ratio=success_ratio,
            latency_avg_ms=latency_avg,
            latency_p50_ms=p50,
            latency_p95_ms=p95,
            latency_p99_ms=p99,
            throughput_per_min=throughput_per_min,
            accuracy_avg=accuracy_avg,
            accuracy_min=accuracy_min,
        )


# ------------------------------
# 병목 감지기
# ------------------------------

class BottleneckDetector:
    def __init__(
        self,
        latency_p95_threshold_ms: float = 500.0,
        accuracy_threshold: float = 0.85,
        throughput_min_threshold_per_min: Optional[float] = None,
    ) -> None:
        self.latency_p95_threshold_ms = latency_p95_threshold_ms
        self.accuracy_threshold = accuracy_threshold
        self.throughput_min_threshold_per_min = throughput_min_threshold_per_min

    def analyze(self, stats: OperationStats) -> List[str]:
        issues: List[str] = []
        if stats.latency_p95_ms > self.latency_p95_threshold_ms:
            issues.append("high_latency_p95")
        if stats.accuracy_avg is not None and stats.accuracy_avg < self.accuracy_threshold:
            issues.append("low_accuracy")
        if (
            self.throughput_min_threshold_per_min is not None
            and stats.throughput_per_min < self.throughput_min_threshold_per_min
        ):
            issues.append("low_throughput")
        return issues


# ------------------------------
# 리소스 매니저
# ------------------------------

class ResourceManager:
    def __init__(self) -> None:
        self.platform = platform.system().lower()

    def set_process_priority(self, nice_value: int) -> bool:
        """
        프로세스 우선순위를 설정합니다. Linux의 경우 nice 값 사용.
        값이 낮을수록 높은 우선순위 (root 필요할 수 있음).
        """
        try:
            if psutil is not None:
                p = psutil.Process(os.getpid())
                p.nice(nice_value)
                logger.info(f"Set process nice to {nice_value}")
                return True
            # psutil 없을 때는 os.nice는 증분(additive)이라 안전하지 않아 생략
            logger.warning("psutil 미설치: nice 변경 생략")
            return False
        except Exception as e:
            logger.warning(f"우선순위 설정 실패: {e}")
            return False

    def set_cpu_affinity(self, cpu_indices: List[int]) -> bool:
        try:
            if psutil is None:
                logger.warning("psutil 미설치: CPU affinity 설정 생략")
                return False
            p = psutil.Process(os.getpid())
            available = list(range(psutil.cpu_count() or 1))
            cpus = [c for c in cpu_indices if c in available]
            if not cpus:
                logger.warning("유효한 CPU 인덱스가 없습니다")
                return False
            p.cpu_affinity(cpus)
            logger.info(f"Set CPU affinity to {cpus}")
            return True
        except Exception as e:
            logger.warning(f"CPU affinity 설정 실패: {e}")
            return False

    def set_oom_score_adj(self, value: int) -> bool:
        """
        /proc/self/oom_score_adj에 쓰기. root 권한 필요할 수 있음.
        범위: -1000(보호) ~ 1000(강제 종료 우선)
        """
        try:
            path = "/proc/self/oom_score_adj"
            with open(path, "w") as f:
                f.write(str(int(value)))
            logger.info(f"Set oom_score_adj to {value}")
            return True
        except Exception as e:
            logger.warning(f"oom_score_adj 설정 실패: {e}")
            return False


# ------------------------------
# 트렌드 분석기
# ------------------------------

class TrendAnalyzer:
    def __init__(self, min_points: int = 5) -> None:
        self.min_points = min_points

    def linear_trend(self, points: List[Tuple[float, float]]) -> Optional[float]:
        """
        points: (t_seconds_epoch, value)
        return: slope per minute
        """
        try:
            if len(points) < self.min_points:
                return None
            t0 = points[0][0]
            xs = [(t - t0) / 60.0 for t, _ in points]  # minutes since start
            ys = [v for _, v in points]
            n = len(xs)
            x_mean = sum(xs) / n
            y_mean = sum(ys) / n
            num = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
            den = sum((xs[i] - x_mean) ** 2 for i in range(n)) or 1e-9
            return num / den
        except Exception as e:
            logger.warning(f"트렌드 계산 실패: {e}")
            return None


# ------------------------------
# 제안 엔진
# ------------------------------

class SuggestionEngine:
    def __init__(self) -> None:
        self._last_suggestions: List[Dict[str, Any]] = []

    def build_suggestions(
        self,
        service: str,
        operation: str,
        stats: OperationStats,
        issues: List[str],
        cpu_utilization: Optional[float],
        mem_utilization: Optional[float],
    ) -> List[Dict[str, Any]]:
        suggestions: List[Dict[str, Any]] = []
        for issue in issues:
            if issue == "high_latency_p95":
                action = {
                    "type": "increase_priority",
                    "params": {"nice": -5},
                    "apply": True,
                }
                suggestions.append({
                    "service": service,
                    "operation": operation,
                    "issue": issue,
                    "reason": f"p95 latency {stats.latency_p95_ms:.1f}ms",
                    "actions": [action, {"type": "pin_cpu", "params": {"cpus": [0]}, "apply": False}],
                    "notes": "핫 경로를 높은 우선순위로, 필요 시 CPU pinning 고려",
                })
            elif issue == "low_accuracy":
                suggestions.append({
                    "service": service,
                    "operation": operation,
                    "issue": issue,
                    "reason": f"avg accuracy {stats.accuracy_avg}",
                    "actions": [
                        {"type": "reduce_batch_or_enable_quality_mode", "apply": False},
                        {"type": "model_recalibration", "apply": False},
                    ],
                    "notes": "정확도 개선을 위한 품질 모드/재보정 제안",
                })
            elif issue == "low_throughput":
                suggestions.append({
                    "service": service,
                    "operation": operation,
                    "issue": issue,
                    "reason": f"throughput {stats.throughput_per_min:.2f}/min",
                    "actions": [
                        {"type": "increase_concurrency", "apply": False},
                        {"type": "enable_caching", "apply": False},
                    ],
                    "notes": "처리량 증대를 위한 병렬성/캐시 제안",
                })

        # 시스템 리소스 기반 일반 제안
        if cpu_utilization is not None and cpu_utilization > 85.0:
            suggestions.append({
                "issue": "high_cpu_utilization",
                "reason": f"CPU {cpu_utilization:.1f}%",
                "actions": [{"type": "pin_cpu", "params": {"cpus": [0]}, "apply": False}],
            })
        if mem_utilization is not None and mem_utilization > 85.0:
            suggestions.append({
                "issue": "high_memory_utilization",
                "reason": f"Memory {mem_utilization:.1f}%",
                "actions": [{"type": "increase_oom_protection", "params": {"oom_score_adj": -100}, "apply": False}],
            })

        self._last_suggestions = suggestions
        return suggestions

    def last_suggestions(self) -> List[Dict[str, Any]]:
        return self._last_suggestions


# ------------------------------
# 메인 모니터
# ------------------------------

class PerformanceMonitor:
    def __init__(
        self,
        window_seconds: int = 300,
        history_capacity: int = 240,  # 약 2시간치(30초 간격 기준)
        analysis_interval_seconds: int = 30,
        latency_p95_threshold_ms: float = 500.0,
        accuracy_threshold: float = 0.85,
        throughput_min_threshold_per_min: Optional[float] = None,
        enable_background_controller: bool = True,
    ) -> None:
        self.window_seconds = int(window_seconds)
        self.history_capacity = int(history_capacity)
        self.analysis_interval_seconds = int(analysis_interval_seconds)

        self._buffers: Dict[str, Dict[str, RollingWindowBuffer]] = defaultdict(lambda: defaultdict(lambda: RollingWindowBuffer(self.window_seconds)))
        self._history_snapshots: Deque[Dict[str, Any]] = deque(maxlen=self.history_capacity)

        self._bottleneck_detector = BottleneckDetector(
            latency_p95_threshold_ms=latency_p95_threshold_ms,
            accuracy_threshold=accuracy_threshold,
            throughput_min_threshold_per_min=throughput_min_threshold_per_min,
        )
        self._resource_manager = ResourceManager()
        self._trend_analyzer = TrendAnalyzer()
        self._suggestion_engine = SuggestionEngine()

        self._controller_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        if enable_background_controller:
            self.start_background_controller()

        logger.info("성능 모니터 초기화 완료")

    # -------- 메트릭 기록 --------
    def record_event(
        self,
        service_name: str,
        operation_name: str,
        latency_ms: float,
        success: bool,
        accuracy: Optional[float] = None,
        timestamp_ms: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        ts = timestamp_ms if timestamp_ms is not None else time.time() * 1000.0
        event = MetricEvent(
            service_name=service_name,
            operation_name=operation_name,
            timestamp_ms=ts,
            latency_ms=float(latency_ms),
            success=bool(success),
            accuracy=accuracy,
            extra=extra or {},
        )
        self._buffers[service_name][operation_name].add_event(event)

    # -------- 데코레이터/컨텍스트 --------
    def instrument_operation(
        self,
        service_name: str,
        operation_name: str,
        accuracy_extractor: Optional[Callable[[Any], Optional[float]]] = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        함수/메서드를 계측하는 데코레이터. 동기/비동기 모두 지원.
        accuracy_extractor(result) -> Optional[float] 로 정확도 추출 가능.
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if asyncio.iscoroutinefunction(func):

                async def wrapper(*args: Any, **kwargs: Any) -> Any:
                    start = time.time()
                    success = True
                    accuracy: Optional[float] = None
                    try:
                        result = await func(*args, **kwargs)
                        if accuracy_extractor is not None:
                            try:
                                accuracy = accuracy_extractor(result)
                            except Exception:
                                accuracy = None
                        else:
                            if isinstance(result, dict) and "accuracy" in result:
                                accuracy = result.get("accuracy")  # type: ignore
                        return result
                    except Exception:
                        success = False
                        raise
                    finally:
                        end = time.time()
                        self.record_event(
                            service_name=service_name,
                            operation_name=operation_name,
                            latency_ms=(end - start) * 1000.0,
                            success=success,
                            accuracy=accuracy,
                        )

                return wrapper
            else:

                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    start = time.time()
                    success = True
                    accuracy: Optional[float] = None
                    try:
                        result = func(*args, **kwargs)
                        if accuracy_extractor is not None:
                            try:
                                accuracy = accuracy_extractor(result)
                            except Exception:
                                accuracy = None
                        else:
                            if isinstance(result, dict) and "accuracy" in result:
                                accuracy = result.get("accuracy")  # type: ignore
                        return result
                    except Exception:
                        success = False
                        raise
                    finally:
                        end = time.time()
                        self.record_event(
                            service_name=service_name,
                            operation_name=operation_name,
                            latency_ms=(end - start) * 1000.0,
                            success=success,
                            accuracy=accuracy,
                        )

                return wrapper

        return decorator

    class _Span:
        def __init__(self, parent: "PerformanceMonitor", service: str, operation: str) -> None:
            self._parent = parent
            self._service = service
            self._operation = operation
            self._start = time.time()
            self._accuracy: Optional[float] = None
            self._success = True

        def set_accuracy(self, accuracy: Optional[float]) -> None:
            self._accuracy = accuracy

        def set_success(self, success: bool) -> None:
            self._success = bool(success)

        def __enter__(self) -> "PerformanceMonitor._Span":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            if exc is not None:
                self._success = False
            end = time.time()
            self._parent.record_event(
                service_name=self._service,
                operation_name=self._operation,
                latency_ms=(end - self._start) * 1000.0,
                success=self._success,
                accuracy=self._accuracy,
            )

    def monitor_span(self, service_name: str, operation_name: str) -> "PerformanceMonitor._Span":
        return PerformanceMonitor._Span(self, service_name, operation_name)

    # -------- 스냅샷/이력/트렌드 --------
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        snapshot: Dict[str, Any] = {"services": {}, "resources": {}}
        for svc, ops in self._buffers.items():
            snapshot["services"].setdefault(svc, {})
            for op, buf in ops.items():
                stats = buf.compute_stats()
                snapshot["services"][svc][op] = stats.__dict__ if stats else None

        # 시스템 리소스
        cpu_util = None
        mem_util = None
        try:
            if psutil is not None:
                cpu_util = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                mem_util = float(mem.percent)
        except Exception:
            cpu_util = None
            mem_util = None

        snapshot["resources"]["cpu_utilization_percent"] = cpu_util
        snapshot["resources"]["memory_utilization_percent"] = mem_util
        snapshot["timestamp"] = time.time()
        return snapshot

    def _append_history(self, snapshot: Dict[str, Any]) -> None:
        self._history_snapshots.append(snapshot)

    def get_trends(self) -> Dict[str, Any]:
        """
        최근 이력으로부터 간단한 선형 추세(분당 변화량)를 계산합니다.
        latency_p95_ms, throughput_per_min, accuracy_avg 등에 대해 계산.
        """
        trends: Dict[str, Any] = {}
        try:
            by_key_points: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
            for snap in self._history_snapshots:
                t = snap.get("timestamp", time.time())
                services = snap.get("services", {})
                for svc, ops in services.items():
                    for op, st in ops.items():
                        if not st:
                            continue
                        key_lat = f"{svc}.{op}.latency_p95_ms"
                        key_thr = f"{svc}.{op}.throughput_per_min"
                        key_acc = f"{svc}.{op}.accuracy_avg"
                        by_key_points[key_lat].append((t, float(st.get("latency_p95_ms", 0.0))))
                        by_key_points[key_thr].append((t, float(st.get("throughput_per_min", 0.0))))
                        acc = st.get("accuracy_avg")
                        if acc is not None:
                            by_key_points[key_acc].append((t, float(acc)))

            for key, pts in by_key_points.items():
                slope = self._trend_analyzer.linear_trend(pts)
                if slope is not None:
                    trends[key] = {"slope_per_min": slope}
        except Exception as e:
            logger.warning(f"트렌드 분석 실패: {e}")
        return trends

    # -------- 병목/제안/제어 --------
    def analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        issues_all: List[Dict[str, Any]] = []
        snapshot = self.get_metrics_snapshot()
        for svc, ops in snapshot.get("services", {}).items():
            for op, st in ops.items():
                if not st:
                    continue
                stats = OperationStats(**st)
                issues = self._bottleneck_detector.analyze(stats)
                if not issues:
                    continue
                issues_all.append({
                    "service": svc,
                    "operation": op,
                    "issues": issues,
                    "stats": st,
                })
        return issues_all

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        snapshot = self.get_metrics_snapshot()
        cpu_util = snapshot.get("resources", {}).get("cpu_utilization_percent")
        mem_util = snapshot.get("resources", {}).get("memory_utilization_percent")
        suggestions: List[Dict[str, Any]] = []
        for svc, ops in snapshot.get("services", {}).items():
            for op, st in ops.items():
                if not st:
                    continue
                stats = OperationStats(**st)
                issues = self._bottleneck_detector.analyze(stats)
                suggestions.extend(
                    self._suggestion_engine.build_suggestions(svc, op, stats, issues, cpu_util, mem_util)
                )
        return suggestions

    def apply_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """
        제안 중 적용 가능한 리소스 관련 액션을 실제로 적용합니다.
        안전을 위해 기본적으로는 공격적 변경은 적용=False로 반환됩니다.
        """
        try:
            actions = suggestion.get("actions", [])
            applied_any = False
            for action in actions:
                if not action.get("apply", False):
                    continue
                action_type = action.get("type")
                params = action.get("params", {})
                if action_type == "increase_priority":
                    nice = int(params.get("nice", -5))
                    applied_any = self._resource_manager.set_process_priority(nice) or applied_any
                elif action_type == "pin_cpu":
                    cpus = params.get("cpus") or []
                    applied_any = self._resource_manager.set_cpu_affinity(list(map(int, cpus))) or applied_any
                elif action_type == "increase_oom_protection":
                    val = int(params.get("oom_score_adj", -100))
                    applied_any = self._resource_manager.set_oom_score_adj(val) or applied_any
            return applied_any
        except Exception as e:
            logger.warning(f"제안 적용 실패: {e}")
            return False

    # -------- 백그라운드 컨트롤러 --------
    def start_background_controller(self) -> None:
        if self._controller_thread and self._controller_thread.is_alive():
            return
        self._stop_event.clear()
        self._controller_thread = threading.Thread(target=self._controller_loop, name="performance-controller", daemon=True)
        self._controller_thread.start()

    def stop_background_controller(self) -> None:
        self._stop_event.set()
        if self._controller_thread:
            self._controller_thread.join(timeout=2.0)

    def _controller_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                snapshot = self.get_metrics_snapshot()
                self._append_history(snapshot)
                suggestions = self.get_optimization_suggestions()
                # 안전한 자동 적용: 우선순위 상향만 제한적으로 적용
                for s in suggestions:
                    for a in s.get("actions", []):
                        if a.get("type") == "increase_priority":
                            a["apply"] = True
                for s in suggestions:
                    self.apply_suggestion(s)
            except Exception as e:
                logger.debug(f"컨트롤러 루프 오류: {e}")
            finally:
                time.sleep(self.analysis_interval_seconds)


__all__ = [
    "PerformanceMonitor",
    "MetricEvent",
    "OperationStats",
]

