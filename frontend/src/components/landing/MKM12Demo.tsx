'use client';

import React, { useEffect, useRef, useState } from 'react';

interface MKM12DemoProps {
  className?: string;
}

export default function MKM12Demo({ className = '' }: MKM12DemoProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [solarValue, setSolarValue] = useState(0.5);
  const [lunarValue, setLunarValue] = useState(0.5);
  const [kineticValue, setKineticValue] = useState(0.5);
  const [crypticValue, setCrypticValue] = useState(0.5);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Three.js 초기화
    const initThreeJS = () => {
      const scene = new (window as any).THREE.Scene();
      const camera = new (window as any).THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      const renderer = new (window as any).THREE.WebGLRenderer({ canvas: canvasRef.current, alpha: true });
      
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      
      // 파티클 시스템 설정
      const particleCount = 2000;
      const geometry = new (window as any).THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      const colors = new Float32Array(particleCount * 3);
      
      for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 10;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
        
        colors[i * 3] = Math.random();
        colors[i * 3 + 1] = Math.random();
        colors[i * 3 + 2] = Math.random();
      }
      
      geometry.setAttribute('position', new (window as any).THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new (window as any).THREE.BufferAttribute(colors, 3));
      
      const material = new (window as any).THREE.PointsMaterial({
        size: 0.1,
        vertexColors: true,
        blending: (window as any).THREE.AdditiveBlending,
        transparent: true,
        opacity: 0.7
      });
      
      const particles = new (window as any).THREE.Points(geometry, material);
      scene.add(particles);
      
      camera.position.z = 5;
      
      // 애니메이션 루프
      const animate = () => {
        requestAnimationFrame(animate);
        
        particles.rotation.x += 0.0005;
        particles.rotation.y += 0.001;
        
        // MKM12 값에 따른 파티클 색상 변화
        updateParticleColors(geometry, solarValue, lunarValue, kineticValue, crypticValue);
        
        renderer.render(scene, camera);
      };
      
      animate();
      
      // 윈도우 리사이즈 처리
      const handleResize = () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      };
      
      window.addEventListener('resize', handleResize);
      
      return () => {
        window.removeEventListener('resize', handleResize);
      };
    };

    // Three.js 라이브러리 로드 확인 후 초기화
    if ((window as any).THREE) {
      initThreeJS();
    } else {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
      script.onload = initThreeJS;
      document.head.appendChild(script);
    }
  }, [solarValue, lunarValue, kineticValue, crypticValue]);

  const updateParticleColors = (geometry: any, solar: number, lunar: number, kinetic: number, cryptic: number) => {
    const colors = geometry.attributes.color.array;
    const totalValue = solar + lunar + kinetic + cryptic;
    
    for (let i = 0; i < colors.length; i += 3) {
      let r = 0, g = 0, b = 0;
      
      const bias = (Math.random() - 0.5) * 0.2;
      
      if (Math.random() < solar + bias) {
        r += 1.0; g += 0.96; b += 0.62; // Yellowish
      }
      if (Math.random() < lunar + bias) {
        r += 0.62; g += 0.78; b += 1.0; // Bluish
      }
      if (Math.random() < kinetic + bias) {
        r += 0.65; g += 0.96; b += 0.76; // Greenish
      }
      if (Math.random() < cryptic + bias) {
        r += 1.0; g += 0.63; b += 0.63; // Reddish
      }
      
      colors[i] = Math.min(r, 1);
      colors[i + 1] = Math.min(g, 1);
      colors[i + 2] = Math.min(b, 1);
    }
    
    geometry.attributes.color.needsUpdate = true;
  };

  const handlePlayMusic = async () => {
    if (!isPlaying) {
      // Tone.js 초기화 및 음악 시작
      if ((window as any).Tone) {
        await (window as any).Tone.start();
        setIsPlaying(true);
        // 여기에 실제 음악 재생 로직 추가
      } else {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js';
        script.onload = async () => {
          await (window as any).Tone.start();
          setIsPlaying(true);
        };
        document.head.appendChild(script);
      }
    } else {
      setIsPlaying(false);
      // 음악 정지 로직
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Three.js 캔버스 */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ zIndex: 1 }}
      />
      
      {/* UI 컨테이너 */}
      <div className="relative z-10 flex flex-col items-center justify-center w-full h-full text-white p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            MKM12 동역학 체험
          </h2>
          <p className="text-gray-300 text-lg max-w-2xl">
            슬라이더를 움직여 MKM12 4가지 힘의 변화를 시각적으로 경험하세요
          </p>
        </div>

        {/* 슬라이더 컨테이너 */}
        <div className="w-full max-w-md bg-black/20 backdrop-blur-md p-6 rounded-2xl border border-white/20">
          <div className="space-y-6">
            <div>
              <label className="block text-yellow-300 font-semibold mb-2">
                S (태양적 힘) - {Math.round(solarValue * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={solarValue}
                onChange={(e) => setSolarValue(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
            
            <div>
              <label className="block text-blue-300 font-semibold mb-2">
                L (태음적 힘) - {Math.round(lunarValue * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={lunarValue}
                onChange={(e) => setLunarValue(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
            
            <div>
              <label className="block text-green-300 font-semibold mb-2">
                K (소양적 힘) - {Math.round(kineticValue * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={kineticValue}
                onChange={(e) => setKineticValue(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
            
            <div>
              <label className="block text-red-300 font-semibold mb-2">
                C (소음적 힘) - {Math.round(crypticValue * 100)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={crypticValue}
                onChange={(e) => setCrypticValue(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
            </div>
          </div>
          
          <button
            onClick={handlePlayMusic}
            className={`mt-6 w-full py-3 px-6 rounded-full font-bold transition-all duration-300 ${
              isPlaying
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-purple-600 hover:bg-purple-700'
            }`}
          >
            {isPlaying ? '음악 정지' : '음악 시작'}
          </button>
        </div>
        
        <p className="mt-4 text-gray-400 text-sm text-center max-w-md">
          이 데모는 MKM12 이론의 시각적 표현입니다. 
          실제 건강 분석을 위해서는 엔오건강도우미 서비스를 이용해주세요.
        </p>
      </div>
    </div>
  );
}
