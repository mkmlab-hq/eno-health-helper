import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: "healthy",
    services: {
      fusion_analyzer: "ready",
      rppg_analyzer: "ready", 
      voice_analyzer: "ready",
      health_analyzer: "ready"
    },
    timestamp: new Date().toISOString()
  });
}
