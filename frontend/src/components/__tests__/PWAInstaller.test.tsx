import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import PWAInstaller from '../PWAInstaller'

// Service Worker 모킹
const mockRegister = jest.fn()
Object.defineProperty(navigator, 'serviceWorker', {
  value: {
    register: mockRegister,
  },
  writable: true,
})

// MediaDevices 모킹
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: jest.fn(() => Promise.resolve('mock-stream')),
    enumerateDevices: jest.fn(() => Promise.resolve([])),
  },
  writable: true,
})

describe('PWAInstaller', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockRegister.mockResolvedValue({
      addEventListener: jest.fn(),
    })
  })

  it('PWA 지원이 없는 경우 렌더링되지 않음', () => {
    // Service Worker 지원 제거
    delete (navigator as any).serviceWorker
    
    render(<PWAInstaller />)
    
    expect(screen.queryByText('앱으로 설치')).not.toBeInTheDocument()
  })

  it('PWA 지원이 있는 경우 Service Worker 등록', async () => {
    render(<PWAInstaller />)
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith('/sw.js')
    })
  })

  it('이미 설치된 경우 설치 완료 메시지 표시', () => {
    // standalone 모드 시뮬레이션
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(display-mode: standalone)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    })

    render(<PWAInstaller />)
    
    expect(screen.getByText('앱으로 설치됨')).toBeInTheDocument()
  })

  it('설치 프롬프트가 표시되는 경우 설치 버튼 렌더링', () => {
    // beforeinstallprompt 이벤트 시뮬레이션
    const mockPrompt = jest.fn()
    const mockUserChoice = Promise.resolve({ outcome: 'accepted' })
    
    const beforeInstallPromptEvent = new Event('beforeinstallprompt') as any
    beforeInstallPromptEvent.prompt = mockPrompt
    beforeInstallPromptEvent.userChoice = mockUserChoice
    
    render(<PWAInstaller />)
    
    // 이벤트 발생
    window.dispatchEvent(beforeInstallPromptEvent)
    
    expect(screen.getByText('앱으로 설치')).toBeInTheDocument()
    expect(screen.getByText('홈 화면에 추가')).toBeInTheDocument()
  })

  it('설치 버튼 클릭 시 설치 프롬프트 실행', async () => {
    const mockPrompt = jest.fn()
    const mockUserChoice = Promise.resolve({ outcome: 'accepted' })
    
    const beforeInstallPromptEvent = new Event('beforeinstallprompt') as any
    beforeInstallPromptEvent.prompt = mockPrompt
    beforeInstallPromptEvent.userChoice = mockUserChoice
    
    render(<PWAInstaller />)
    
    // 이벤트 발생
    window.dispatchEvent(beforeInstallPromptEvent)
    
    // 설치 버튼 클릭
    const installButton = screen.getByText('앱으로 설치')
    fireEvent.click(installButton)
    
    await waitFor(() => {
      expect(mockPrompt).toHaveBeenCalled()
    })
  })
})
