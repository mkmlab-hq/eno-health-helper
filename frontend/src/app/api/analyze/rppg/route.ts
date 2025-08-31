import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // 실제 구현에서는 여기에 rPPG 분석 로직 추가
    return NextResponse.json({
      status: 'success',
      data: {
        heartRate: 75,
        stressIndex: 0.3,
        confidence: 0.85,
        quality: 'good',
        frameCount: 300
      }
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
