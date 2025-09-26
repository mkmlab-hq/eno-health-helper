import { render, screen, fireEvent } from '@testing-library/react';
import GlobalError from '../global-error';

// Mock console.error to avoid noise in tests
const mockConsoleError = jest.fn();
console.error = mockConsoleError;

describe('GlobalError', () => {
  const mockError = new Error('Global test error message');
  const mockReset = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders global error UI with correct message', () => {
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('치명적 시스템 오류')).toBeInTheDocument();
    expect(screen.getByText('애플리케이션에 심각한 문제가 발생했습니다.')).toBeInTheDocument();
  });

  it('displays error details correctly', () => {
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('에러 정보:')).toBeInTheDocument();
    expect(screen.getByText(/Type:/)).toBeInTheDocument();
    expect(screen.getByText(/Global Error/)).toBeInTheDocument();
    expect(screen.getByText('Global test error message')).toBeInTheDocument();
  });

  it('calls reset function when restart button is clicked', () => {
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    const restartButton = screen.getByText('애플리케이션 재시작');
    fireEvent.click(restartButton);
    
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it('reloads page when refresh button is clicked', () => {
    const mockReload = jest.fn();
    Object.defineProperty(window, 'location', {
      value: { reload: mockReload },
      writable: true,
    });
    
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    const refreshButton = screen.getByText('페이지 새로고침');
    fireEvent.click(refreshButton);
    
    expect(mockReload).toHaveBeenCalledTimes(1);
  });

  it('displays error digest when available', () => {
    const errorWithDigest = new Error('Global test error') as Error & { digest?: string };
    errorWithDigest.digest = 'global-test-digest-456';
    
    render(<GlobalError error={errorWithDigest} reset={mockReset} />);
    
    expect(screen.getByText('오류 ID: global-test-digest-456')).toBeInTheDocument();
  });

  it('displays fallback error ID when digest is not available', () => {
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('오류 ID: GLOBAL-ERROR')).toBeInTheDocument();
  });

  it('logs global error to console', () => {
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    expect(mockConsoleError).toHaveBeenCalledWith('Global Application Error:', mockError);
  });

  it('displays emergency contact information', () => {
    render(<GlobalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('🚨 긴급 상황입니다')).toBeInTheDocument();
    expect(screen.getByText('이 오류가 지속되면 즉시 시스템 관리자에게 연락하세요')).toBeInTheDocument();
  });

  it('renders with proper container structure', () => {
    const { container } = render(<GlobalError error={mockError} reset={mockReset} />);
    
    // 메인 컨테이너가 존재하는지 확인
    expect(container.firstChild).toHaveClass('min-h-screen');
    expect(container.firstChild).toHaveClass('bg-gradient-to-br');
  });
});
