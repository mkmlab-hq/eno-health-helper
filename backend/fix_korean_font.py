#!/usr/bin/env python3
"""
한글 폰트 문제 해결 스크립트
matplotlib에서 한글 텍스트가 깨지는 문제를 수정합니다.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import os

def fix_korean_font():
    """한글 폰트 문제를 해결합니다."""
    
    system = platform.system()
    
    if system == "Windows":
        # Windows에서 한글 폰트 찾기
        font_paths = [
            "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
            "C:/Windows/Fonts/gulim.ttc",   # 굴림
            "C:/Windows/Fonts/batang.ttc",  # 바탕
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'Gulim', 'Batang']
                print(f"✅ 한글 폰트 설정 완료: {font_path}")
                return True
                
    elif system == "Darwin":  # macOS
        plt.rcParams['font.family'] = 'AppleGothic'
        print("✅ macOS 한글 폰트 설정 완료")
        return True
        
    elif system == "Linux":
        # Linux에서 한글 폰트 찾기
        font_paths = [
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = ['NanumGothic', 'Noto Sans CJK JP']
                print(f"✅ Linux 한글 폰트 설정 완료: {font_path}")
                return True
    
    # 폰트를 찾지 못한 경우 기본 설정
    plt.rcParams['font.family'] = 'DejaVu Sans'
    print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    return False

def test_korean_plot():
    """한글 폰트가 제대로 작동하는지 테스트합니다."""
    try:
        fix_korean_font()
        
        # 테스트 그래프 생성
        plt.figure(figsize=(10, 6))
        plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
        plt.title('한글 폰트 테스트 - RPPG 정확도 향상')
        plt.xlabel('에포크')
        plt.ylabel('정확도 (%)')
        plt.grid(True, alpha=0.3)
        
        # 파일로 저장
        plt.savefig('korean_font_test.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ 한글 폰트 테스트 완료: korean_font_test.png")
        return True
        
    except Exception as e:
        print(f"❌ 한글 폰트 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔧 한글 폰트 문제 해결 시작...")
    success = test_korean_plot()
    
    if success:
        print("🎉 한글 폰트 문제 해결 완료!")
    else:
        print("⚠️ 한글 폰트 문제 해결 실패. 기본 폰트를 사용합니다.") 