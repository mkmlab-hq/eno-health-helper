#!/usr/bin/env python3
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np

# Ensure backend app services are importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
APP_SERVICES_DIR = BACKEND_DIR / "app" / "services"
if str(BACKEND_DIR) not in sys.path:
	sys.path.insert(0, str(BACKEND_DIR))
if str(APP_SERVICES_DIR) not in sys.path:
	sys.path.insert(0, str(APP_SERVICES_DIR))

# Conditional librosa import for optional baseline
try:
	import librosa  # type: ignore
	_HAS_LIBROSA = True
except Exception:
	_HAS_LIBROSA = False

# Import analyzers
try:
	from app.services.rppg_analyzer import MedicalGradeRPPGAnalyzer  # type: ignore
except Exception:
	MedicalGradeRPPGAnalyzer = None  # type: ignore

try:
	from app.services.real_voice_analyzer import RealVoiceAnalyzer  # type: ignore
except Exception:
	# Fallback: import directly from services folder on sys.path
	try:
		import real_voice_analyzer as _rva  # type: ignore
		RealVoiceAnalyzer = _rva.RealVoiceAnalyzer  # type: ignore
	except Exception:
		# Final fallback: import via importlib from absolute path
		try:
			import importlib.util
			_rva_path = APP_SERVICES_DIR / "real_voice_analyzer.py"
			spec = importlib.util.spec_from_file_location("bench_rva", str(_rva_path))
			module = importlib.util.module_from_spec(spec) if spec else None
			if spec and spec.loader and module:
				spec.loader.exec_module(module)
				RealVoiceAnalyzer = getattr(module, "RealVoiceAnalyzer", None)
			else:
				RealVoiceAnalyzer = None  # type: ignore
		except Exception:
			RealVoiceAnalyzer = None  # type: ignore

# Prefer RealRPPGAnalyzer (no SciPy) for baseline
try:
	from app.services.real_rppg_analyzer import RealRPPGAnalyzer  # type: ignore
except Exception:
	try:
		import real_rppg_analyzer as _rra  # type: ignore
		RealRPPGAnalyzer = _rra.RealRPPGAnalyzer  # type: ignore
	except Exception:
		RealRPPGAnalyzer = None  # type: ignore


def generate_synthetic_video_frames(num_frames: int = 300, width: int = 640, height: int = 480) -> List[np.ndarray]:
	"""Generate synthetic frames with subtle green-channel modulation to simulate rPPG."""
	frames: List[np.ndarray] = []
	t = np.linspace(0, num_frames / 30.0, num_frames)
	# 72 BPM ~ 1.2 Hz signal
	signal = 0.1 * np.sin(2 * np.pi * 1.2 * t)
	for i in range(num_frames):
		# Base image gray background
		frame = np.full((height, width, 3), 120, dtype=np.uint8)
		# Draw a simple face-like ellipse to provide structure (Haar may still fail; used for timing only)
		center = (width // 2, height // 2)
		axes = (width // 6, height // 5)
		color = (200, 200, 200)
		import cv2  # local import to avoid hard dependency if OpenCV is missing when only voice is tested
		cv2.ellipse(frame, center, axes, 0, 0, 360, color, -1)
		# Apply small green modulation in a central ROI
		y0, y1 = height // 3, 2 * height // 3
		x0, x1 = width // 3, 2 * width // 3
		g = frame[y0:y1, x0:x1, 1].astype(np.float32)
		g = np.clip(g * (1.0 + signal[i]), 0, 255)
		frame[y0:y1, x0:x1, 1] = g.astype(np.uint8)
		frames.append(frame)
	return frames


def generate_synthetic_audio(duration_s: float = 5.0, sample_rate: int = 44100) -> np.ndarray:
	"""Generate synthetic voiced signal with harmonics and noise."""
	n = int(duration_s * sample_rate)
	t = np.linspace(0, duration_s, n, endpoint=False)
	base_f0 = 150.0
	s = np.sin(2 * np.pi * base_f0 * t)
	s += 0.3 * np.sin(2 * np.pi * 2 * base_f0 * t)
	s += 0.2 * np.sin(2 * np.pi * 3 * base_f0 * t)
	s += 0.05 * np.random.randn(n)
	s = s / np.max(np.abs(s))
	return s.astype(np.float32)


def timeit(fn, *args, **kwargs) -> Tuple[float, Any]:
	start = time.perf_counter()
	result = fn(*args, **kwargs)
	elapsed = time.perf_counter() - start
	return elapsed, result


def benchmark_rppg() -> Dict[str, Any]:
	metrics: Dict[str, Any] = {}
	# Prefer RealRPPGAnalyzer for a SciPy-free baseline
	metrics["available"] = RealRPPGAnalyzer is not None
	if RealRPPGAnalyzer is None:
		metrics["error"] = "RealRPPGAnalyzer import failed"
		return metrics

	analyzer = RealRPPGAnalyzer()
	frame_count = 300
	video_bytes = b"synthetic_video_data" * 100

	# Use E2E path (internally simulates ROI + processing)
	e2e_time, result = timeit(analyzer.analyze_video_frames, video_bytes, frame_count)
	metrics["e2e_sec"] = round(e2e_time, 6)
	metrics["result"] = result

	# Step timings where possible using internal helpers with simulated data
	# Generate the same refined signals pipeline timings
	_, rgb = 0.0, analyzer._extract_rgb_signals_fallback(frame_count)
	ref_time, refined = timeit(analyzer._refine_signals, rgb)
	metrics["refine_sec"] = round(ref_time, 6)
	freq_time, freq = timeit(analyzer._frequency_domain_analysis, refined)
	metrics["freq_analysis_sec"] = round(freq_time, 6)
	hr_time, _hr = timeit(analyzer._calculate_heart_rate_and_hrv, freq)
	metrics["hr_hrv_sec"] = round(hr_time, 6)
	qual_time, _qual = timeit(analyzer._assess_signal_quality, refined, freq)
	metrics["signal_quality_sec"] = round(qual_time, 6)
	return metrics


def benchmark_voice() -> Dict[str, Any]:
	metrics: Dict[str, Any] = {
		"available": RealVoiceAnalyzer is not None
	}
	if RealVoiceAnalyzer is None:
		metrics["error"] = "RealVoiceAnalyzer import failed"
		return metrics

	analyzer = RealVoiceAnalyzer()
	duration = 3.0
	signal = generate_synthetic_audio(duration, analyzer.sample_rate)
	audio_bytes = (signal.tobytes())

	# End-to-end
	e2e_time, result = timeit(analyzer.analyze_audio_data, audio_bytes, duration)
	metrics["e2e_sec"] = round(e2e_time, 6)
	metrics["result"] = result

	# Step timings by calling internals on array
	pre_time, pre = timeit(analyzer._preprocess_signal, signal)
	metrics["preprocess_sec"] = round(pre_time, 6)
	f0_time, f0 = timeit(analyzer._analyze_fundamental_frequency, pre)
	metrics["f0_sec"] = round(f0_time, 6)
	jit_time, jit = timeit(analyzer._analyze_jitter, pre, f0)
	metrics["jitter_sec"] = round(jit_time, 6)
	shim_time, shim = timeit(analyzer._analyze_shimmer, pre, f0)
	metrics["shimmer_sec"] = round(shim_time, 6)
	hnr_time, hnr = timeit(analyzer._analyze_hnr, pre, f0)
	metrics["hnr_sec"] = round(hnr_time, 6)
	return metrics


def benchmark_librosa(signal: np.ndarray, sample_rate: int) -> Dict[str, Any]:
	metrics: Dict[str, Any] = {"available": _HAS_LIBROSA}
	if not _HAS_LIBROSA:
		metrics["error"] = "librosa not available"
		return metrics

	# librosa pipeline baseline: YIN pitch + MFCC extraction
	# Avoid resampling by passing native sr
	proc: Dict[str, Any] = {}
	start = time.perf_counter()
	f0 = librosa.yin(signal, fmin=50, fmax=800, sr=sample_rate)
	proc["yin_sec"] = round(time.perf_counter() - start, 6)

	start = time.perf_counter()
	mfcc = librosa.feature.mfcc(y=signal, sr=sample_rate, n_mfcc=13)
	proc["mfcc_sec"] = round(time.perf_counter() - start, 6)

	proc["f0_mean"] = float(np.nanmean(f0)) if f0.size else float("nan")
	proc["mfcc_shape"] = list(mfcc.shape) if mfcc is not None else []
	return proc


def benchmark_opencv_face_detection() -> Dict[str, Any]:
	"""Benchmark OpenCV Haar cascade face detection on synthetic frames."""
	import cv2  # type: ignore
	frames = generate_synthetic_video_frames(num_frames=60, width=640, height=480)
	gray_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
	cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

	# Warmup
	_ = cascade.detectMultiScale(gray_frames[0], scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

	start = time.perf_counter()
	detections = []
	for g in gray_frames:
		d = cascade.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
		detections.append(len(d))
	elapsed = time.perf_counter() - start

	return {
		"frames": len(gray_frames),
		"total_time_sec": round(elapsed, 6),
		"avg_time_per_frame_ms": round(1000.0 * elapsed / len(gray_frames), 3),
		"avg_detections": float(np.mean(detections)) if detections else 0.0
	}


def main() -> None:
	report: Dict[str, Any] = {"rppg": {}, "voice": {}, "librosa": {}, "opencv_face": {}}

	try:
		report["rppg"] = benchmark_rppg()
	except Exception as e:
		report["rppg"] = {"available": False, "error": str(e)}

	try:
		report["voice"] = benchmark_voice()
	except Exception as e:
		report["voice"] = {"available": False, "error": str(e)}

	try:
		report["opencv_face"] = benchmark_opencv_face_detection()
	except Exception as e:
		report["opencv_face"] = {"available": False, "error": str(e)}

	# librosa baseline (optional)
	try:
		if report.get("voice", {}).get("available"):
			duration = 3.0
			sample_rate = 44100
			sig = generate_synthetic_audio(duration, sample_rate)
			report["librosa"] = benchmark_librosa(sig, sample_rate)
	except Exception as e:
		report["librosa"] = {"available": False, "error": str(e)}

	# Write baseline report
	out_dir = CURRENT_DIR
	out_path = out_dir / "baseline_metrics.json"
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump(report, f, indent=2, ensure_ascii=False)

	print(json.dumps(report, indent=2, ensure_ascii=False))
	print(f"Baseline metrics written to: {out_path}")


if __name__ == "__main__":
	main()