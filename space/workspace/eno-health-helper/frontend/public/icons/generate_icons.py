#!/usr/bin/env python3
"""
PWA 아이콘 생성 스크립트
엔오건강도우미 앱을 위한 다양한 크기의 아이콘 생성
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """지정된 크기의 아이콘 생성"""
    # 새 이미지 생성 (투명 배경)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 배경 원 그리기 (그라데이션 효과)
    margin = size // 10
    circle_size = size - 2 * margin
    
    # 그라데이션 배경 (파란색 계열)
    for i in range(circle_size):
        alpha = int(255 * (1 - i / circle_size))
        color = (0, 150, 255, alpha)
        draw.ellipse([margin + i//2, margin + i//2, 
                     size - margin - i//2, size - margin - i//2], 
                     fill=color)
    
    # 심장 모양 그리기 (중앙)
    heart_size = size // 3
    heart_x = size // 2
    heart_y = size // 2
    
    # 심장 모양 (간단한 원형으로 대체)
    draw.ellipse([heart_x - heart_size//2, heart_y - heart_size//2,
                  heart_x + heart_size//2, heart_y + heart_size//2],
                  fill=(255, 100, 100, 255))
    
    # 텍스트 추가 (작은 크기일 때는 생략)
    if size >= 128:
        try:
            # 폰트 크기 계산
            font_size = max(12, size // 8)
            font = ImageFont.truetype("arial.ttf", font_size)
            text = "ENO"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (size - text_width) // 2
            text_y = heart_y + heart_size//2 + 10
            
            draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
        except:
            pass  # 폰트 로드 실패 시 텍스트 생략
    
    # 파일 저장
    img.save(filename, 'PNG')
    print(f"✅ 아이콘 생성 완료: {filename} ({size}x{size})")

def main():
    """모든 크기의 아이콘 생성"""
    # 생성할 아이콘 크기들
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # icons 디렉토리 생성
    os.makedirs('icons', exist_ok=True)
    
    print("🎨 엔오건강도우미 PWA 아이콘 생성 시작...")
    
    for size in sizes:
        filename = f"icons/icon-{size}x{size}.png"
        create_icon(size, filename)
    
    print("🎉 모든 PWA 아이콘 생성 완료!")
    print("📱 이제 manifest.json에서 아이콘 경로를 확인하세요.")

if __name__ == "__main__":
    main() 