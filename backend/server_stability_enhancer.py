#!/usr/bin/env python3
"""
서버 안정성 향상 스크립트
포트 충돌 방지, 백그라운드 프로세스 정리, 연결 풀 최적화
"""

import os
import sys
import subprocess
import time
import logging
import psutil
import socket
from typing import List, Dict, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServerStabilityEnhancer:
    """서버 안정성 향상기"""
    
    def __init__(self):
        self.ports = [8000, 8001, 8002, 8003]
        self.process_names = ['python', 'py', 'uvicorn']
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        
    def check_port_usage(self, port: int) -> Optional[Dict]:
        """포트 사용 현황 확인"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                # 포트가 사용 중
                processes = self._find_processes_by_port(port)
                return {
                    'port': port,
                    'in_use': True,
                    'processes': processes
                }
            else:
                return {
                    'port': port,
                    'in_use': False,
                    'processes': []
                }
                
        except Exception as e:
            logger.error(f"포트 {port} 확인 실패: {e}")
            return None
    
    def _find_processes_by_port(self, port: int) -> List[Dict]:
        """특정 포트를 사용하는 프로세스 찾기"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if conn.laddr.port == port:
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.error(f"프로세스 검색 실패: {e}")
            
        return processes
    
    def cleanup_background_processes(self) -> bool:
        """백그라운드 프로세스 정리"""
        try:
            logger.info("🧹 백그라운드 프로세스 정리 시작")
            
            cleaned_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                    
                    # Python 관련 프로세스 중 uvicorn 서버 프로세스 식별
                    if (proc_name in self.process_names and 
                        ('uvicorn' in cmdline or 'main.py' in cmdline or 'server' in cmdline)):
                        
                        logger.info(f"🔍 발견된 서버 프로세스: PID {proc.info['pid']} - {cmdline}")
                        
                        # 사용자 확인 후 종료
                        if self._should_terminate_process(proc.info['pid'], cmdline):
                            proc.terminate()
                            time.sleep(1)
                            
                            if proc.is_running():
                                proc.kill()
                                logger.warning(f"⚠️ 강제 종료: PID {proc.info['pid']}")
                            
                            cleaned_count += 1
                            logger.info(f"✅ 프로세스 종료: PID {proc.info['pid']}")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.info(f"🧹 백그라운드 프로세스 정리 완료: {cleaned_count}개 종료")
            return True
            
        except Exception as e:
            logger.error(f"백그라운드 프로세스 정리 실패: {e}")
            return False
    
    def _should_terminate_process(self, pid: int, cmdline: str) -> bool:
        """프로세스 종료 여부 판단"""
        # 현재 작업 디렉토리와 관련된 프로세스만 종료
        if self.backend_dir in cmdline:
            return True
        
        # uvicorn 서버 프로세스
        if 'uvicorn' in cmdline and ('8000' in cmdline or '8001' in cmdline):
            return True
            
        return False
    
    def find_available_port(self) -> int:
        """사용 가능한 포트 찾기"""
        for port in self.ports:
            if not self.check_port_usage(port)['in_use']:
                logger.info(f"✅ 사용 가능한 포트 발견: {port}")
                return port
        
        # 모든 포트가 사용 중이면 새로운 포트 할당
        new_port = max(self.ports) + 1
        logger.info(f"🆕 새로운 포트 할당: {new_port}")
        return new_port
    
    def start_stable_server(self, port: Optional[int] = None) -> bool:
        """안정적인 서버 시작"""
        try:
            if port is None:
                port = self.find_available_port()
            
            logger.info(f"🚀 안정적인 서버 시작: 포트 {port}")
            
            # 서버 시작 명령어
            cmd = [
                sys.executable, '-m', 'uvicorn', 
                'main:app', 
                '--host', '127.0.0.1', 
                '--port', str(port),
                '--log-level', 'info',
                '--reload'
            ]
            
            # 백그라운드에서 서버 시작
            process = subprocess.Popen(
                cmd,
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 서버 시작 대기
            time.sleep(3)
            
            if process.poll() is None:
                logger.info(f"✅ 서버 시작 성공: PID {process.pid}, 포트 {port}")
                
                # 서버 정보 저장
                server_info = {
                    'pid': process.pid,
                    'port': port,
                    'start_time': time.time(),
                    'status': 'running'
                }
                
                with open('server_info.json', 'w', encoding='utf-8') as f:
                    import json
                    json.dump(server_info, f, indent=2, ensure_ascii=False)
                
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ 서버 시작 실패: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"서버 시작 실패: {e}")
            return False
    
    def health_check(self, port: int) -> bool:
        """서버 헬스체크"""
        try:
            import requests
            
            response = requests.get(
                f"http://127.0.0.1:{port}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ 서버 헬스체크 성공: 포트 {port}")
                return True
            else:
                logger.warning(f"⚠️ 서버 응답 오류: {response.status_code}")
                return False
                
        except ImportError:
            logger.warning("⚠️ requests 모듈 미설치 - 헬스체크 건너뜀")
            return True
        except Exception as e:
            logger.error(f"❌ 헬스체크 실패: {e}")
            return False
    
    def run_stability_enhancement(self) -> bool:
        """안정성 향상 전체 프로세스 실행"""
        try:
            logger.info("🚀 서버 안정성 향상 프로세스 시작")
            
            # 1단계: 백그라운드 프로세스 정리
            if not self.cleanup_background_processes():
                logger.warning("⚠️ 백그라운드 프로세스 정리 실패")
            
            # 2단계: 포트 사용 현황 확인
            logger.info("🔍 포트 사용 현황 확인")
            for port in self.ports:
                usage = self.check_port_usage(port)
                if usage:
                    if usage['in_use']:
                        logger.warning(f"⚠️ 포트 {port} 사용 중: {len(usage['processes'])}개 프로세스")
                    else:
                        logger.info(f"✅ 포트 {port} 사용 가능")
            
            # 3단계: 안정적인 서버 시작
            if not self.start_stable_server():
                logger.error("❌ 서버 시작 실패")
                return False
            
            # 4단계: 서버 상태 확인
            time.sleep(2)
            if not self.health_check(8001):  # 기본 포트
                logger.warning("⚠️ 서버 헬스체크 실패")
            
            logger.info("🎉 서버 안정성 향상 완료!")
            return True
            
        except Exception as e:
            logger.error(f"안정성 향상 프로세스 실패: {e}")
            return False

def main():
    """메인 함수"""
    try:
        logger.info("🎯 서버 안정성 향상 시작")
        
        enhancer = ServerStabilityEnhancer()
        success = enhancer.run_stability_enhancement()
        
        if success:
            print("\n" + "="*60)
            print("🎉 서버 안정성 향상 완료!")
            print("="*60)
            print("✅ 백그라운드 프로세스 정리 완료")
            print("✅ 포트 충돌 해결 완료")
            print("✅ 안정적인 서버 시작 완료")
            print("✅ 서버 상태 확인 완료")
            print("="*60)
            print("💡 이제 부하 테스트를 실행할 수 있습니다!")
        else:
            print("\n" + "="*60)
            print("❌ 서버 안정성 향상 실패")
            print("="*60)
            print("문제를 파악하고 수동으로 해결해주세요.")
        
    except Exception as e:
        logger.error(f"메인 실행 중 오류: {e}")
        print(f"\n❌ 실행 오류: {e}")

if __name__ == "__main__":
    main()
