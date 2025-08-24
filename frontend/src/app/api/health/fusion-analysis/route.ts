import { NextRequest, NextResponse } from 'next/server'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function POST(req: NextRequest) {
	try {
		const incomingForm = await req.formData()
		const video = incomingForm.get('video') as unknown as File | null
		const audio = incomingForm.get('audio') as unknown as File | null
		let userId = incomingForm.get('user_id') as string | null

		if (!video || !audio) {
			return NextResponse.json({ error: '비디오와 오디오 파일이 모두 필요합니다.' }, { status: 400 })
		}

		// 기본 사용자 ID 설정
		if (!userId || typeof userId !== 'string' || userId.trim() === '') {
			userId = 'anonymous'
		}

		// 백엔드로 전달할 FormData 구성
		const backendForm = new FormData()
		backendForm.append('video', video, (video as File).name || 'recording.webm')
		backendForm.append('audio', audio, (audio as File).name || 'audio.wav')
		backendForm.append('user_id', userId)

		const controller = new AbortController()
		const timeout = setTimeout(() => controller.abort(), 90_000) // 90s timeout

		try {
			const response = await fetch(`${API_BASE_URL}/api/health/fusion-analysis`, {
				method: 'POST',
				body: backendForm,
				signal: controller.signal,
			})

			const contentType = response.headers.get('content-type') || ''
			const isJson = contentType.includes('application/json')
			const data = isJson ? await response.json() : await response.text()

			if (!response.ok) {
				return NextResponse.json(
					{ error: data?.detail || data || '백엔드 분석 호출 실패' },
					{ status: response.status }
				)
			}

			return NextResponse.json(data)
		} finally {
			clearTimeout(timeout)
		}
	} catch (err: any) {
		const isAbort = err?.name === 'AbortError'
		return NextResponse.json(
			{ error: isAbort ? '요청 시간이 초과되었습니다.' : (err?.message || '서버 오류가 발생했습니다.') },
			{ status: isAbort ? 504 : 500 }
		)
	}
}