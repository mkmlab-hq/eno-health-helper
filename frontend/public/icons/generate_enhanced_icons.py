#!/usr/bin/env python3
"""
엔오건강도우미 향상된 PWA 아이콘 생성 스크립트
디자인 철학: "따뜻한 기술, 직관적인 건강"
- 미래지향적 다크 모드
- Glassmorphism (반투명 유리 질감)
- 청록색/하늘색 네온 효과
- Orbitron 폰트 스타일
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_glassmorphism_icon(size, filename):
    """Glassmorphism 스타일의 향상된 아이콘 생성"""
    # 새 이미지 생성 (투명 배경)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 중앙점 계산
    center = size // 2
    margin = size // 8
    
    # 1. 배경 그라데이션 원 (다크 모드 기반)
    for i in range(size // 2):
        # 다크 그레이에서 블루 그레이로 그라데이션
        alpha = int(100 * (1 - i / (size // 2)))
        color = (20 + i//3, 30 + i//2, 40 + i//2, alpha)
        draw.ellipse([i, i, size - i, size - i], fill=color)
    
    # 2. Glassmorphism 효과 (반투명 유리 질감)
    glass_radius = size // 2 - margin
    glass_center = center
    
    # 외부 테두리 (네온 효과)
    for i in range(3):
        alpha = int(150 * (1 - i / 3))
        neon_color = (0, 200, 255, alpha)  # 청록색 네온
        draw.ellipse([glass_center - glass_radius - i, 
                     glass_center - glass_radius - i,
                     glass_center + glass_radius + i, 
                     glass_center + glass_radius + i], 
                     outline=neon_color, width=2)
    
    # 3. 내부 Glassmorphism 원
    inner_radius = glass_radius - 10
    # 반투명 유리 효과
    glass_color = (100, 150, 200, 80)  # 반투명 블루
    draw.ellipse([glass_center - inner_radius, 
                 glass_center - inner_radius,
                 glass_center + inner_radius, 
                 glass_center + inner_radius], 
                 fill=glass_color)
    
    # 4. 심장 모양 (따뜻한 기술의 상징)
    heart_size = size // 4
    heart_x = center
    heart_y = center
    
    # 심장 모양 그리기 (간단한 원형으로 대체)
    heart_color = (255, 100, 100, 200)  # 따뜻한 빨간색
    draw.ellipse([heart_x - heart_size//2, 
                 heart_y - heart_size//2,
                 heart_x + heart_size//2, 
                 heart_y + heart_size//2],
                 fill=heart_color)
    
    # 5. 네온 효과 추가
    neon_glow = 3
    for i in range(neon_glow):
        alpha = int(100 * (1 - i / neon_glow))
        glow_color = (0, 255, 255, alpha)  # 청록색 네온 글로우
        draw.ellipse([heart_x - heart_size//2 - i, 
                     heart_y - heart_size//2 - i,
                     heart_x + heart_size//2 + i, 
                     heart_y + heart_size//2 + i],
                     outline=glow_color, width=1)
    
    # 6. 텍스트 추가 (Orbitron 스타일)
    if size >= 128:
        try:
            # 폰트 크기 계산
            font_size = max(14, size // 10)
            
            # 기본 폰트 사용 (Orbitron 스타일을 모방)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # "ENO" 텍스트
            text = "ENO"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (size - text_width) // 2
            text_y = heart_y + heart_size//2 + 15
            
            # 텍스트 그림자 효과
            shadow_color = (0, 0, 0, 150)
            draw.text((text_x + 1, text_y + 1), text, fill=shadow_color, font=font)
            
            # 메인 텍스트 (네온 효과)
            main_color = (0, 255, 255, 255)  # 청록색 네온
            draw.text((text_x, text_y), text, fill=main_color, font=font)
            
        except Exception as e:
            print(f"텍스트 추가 실패: {e}")
    
    # 7. 추가 Glassmorphism 효과 (반사광)
    reflection_size = size // 6
    reflection_alpha = 60
    reflection_color = (255, 255, 255, reflection_alpha)
    
    # 왼쪽 상단 반사광
    draw.ellipse([margin, margin, 
                 margin + reflection_size, 
                 margin + reflection_size],
                 fill=reflection_color)
    
    # 파일 저장
    img.save(filename, 'PNG')
    print(f"✅ 향상된 아이콘 생성 완료: {filename} ({size}x{size})")

def main():
    """모든 크기의 향상된 아이콘 생성"""
    # 생성할 아이콘 크기들 (PWA 표준)
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # icons 디렉토리 생성
    os.makedirs('icons', exist_ok=True)
    
    print("🎨 엔오건강도우미 향상된 PWA 아이콘 생성 시작...")
    print("✨ 디자인 철학: '따뜻한 기술, 직관적인 건강'")
    print("🎭 스타일: Glassmorphism + 네온 효과")
    
    for size in sizes:
        filename = f"icons/icon-{size}x{size}.png"
        create_glassmorphism_icon(size, filename)
    
    print("🎉 모든 향상된 PWA 아이콘 생성 완료!")
    print("📱 Glassmorphism + 네온 효과가 적용된 아이콘입니다.")
    print("🔮 이제 manifest.json에서 아이콘 경로를 확인하세요.")

if __name__ == "__main__":
    main() 