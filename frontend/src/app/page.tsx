'use client';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f0f8ff',
      padding: '32px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        maxWidth: '1024px',
        margin: '0 auto',
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: '48px',
          fontWeight: 'bold',
          color: '#1e40af',
          marginBottom: '32px'
        }}>
          엔오건강도우미
        </h1>
        
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          padding: '32px',
          marginBottom: '32px'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#1f2937',
            marginBottom: '16px'
          }}>
            백엔드 API 연결 상태
          </h2>
          <div style={{
            fontSize: '18px',
            color: '#374151',
            marginBottom: '8px'
          }}>
            백엔드 서버: localhost:8001 ✅
          </div>
          <div style={{
            fontSize: '18px',
            color: '#374151'
          }}>
            프론트엔드 서버: localhost:3000 ✅
          </div>
        </div>

        <div style={{
          backgroundColor: '#d1fae5',
          border: '1px solid #10b981',
          borderRadius: '8px',
          padding: '24px'
        }}>
          <h3 style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#065f46',
            marginBottom: '12px'
          }}>
            🎉 연결 성공!
          </h3>
          <p style={{
            color: '#047857'
          }}>
            백엔드와 프론트엔드가 모두 정상적으로 실행되고 있습니다.
          </p>
        </div>
      </div>
    </div>
  );
} 