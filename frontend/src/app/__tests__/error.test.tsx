import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../error';

// Mock console.error to avoid noise in tests
const mockConsoleError = jest.fn();
console.error = mockConsoleError;

describe('ErrorBoundary', () => {
  const mockError = new Error('Test error message');
  const mockReset = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders error UI with correct message', () => {
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('앱 오류가 발생했습니다')).toBeInTheDocument();
    expect(screen.getByText('예상치 못한 문제가 발생했습니다. 다시 시도해주세요.')).toBeInTheDocument();
  });

  it('displays error details in development mode', () => {
    // NODE_ENV를 테스트용으로 변경
    (process.env as any).NODE_ENV = 'development';
    
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('에러 상세 정보:')).toBeInTheDocument();
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    
    (process.env as any).NODE_ENV = 'production';
  });

  it('hides error details in production mode', () => {
    // NODE_ENV를 프로덕션용으로 변경
    (process.env as any).NODE_ENV = 'production';
    
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('앱 오류가 발생했습니다')).toBeInTheDocument();
    expect(screen.queryByText('에러 상세 정보:')).not.toBeInTheDocument();
    expect(screen.queryByText('Test error message')).not.toBeInTheDocument();
    
    // NODE_ENV를 원래대로 복원
    (process.env as any).NODE_ENV = 'test';
  });

  it('calls reset function when retry button is clicked', () => {
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    const retryButton = screen.getByText('다시 시도');
    fireEvent.click(retryButton);
    
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it('navigates to home when home button is clicked', () => {
    const mockLocation = { href: '' };
    Object.defineProperty(window, 'location', {
      value: mockLocation,
      writable: true,
    });
    
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    const homeButton = screen.getByText('홈으로 이동');
    fireEvent.click(homeButton);
    
    expect(mockLocation.href).toBe('/');
  });

  it('displays error digest when available', () => {
    const errorWithDigest = new Error('Test error') as Error & { digest?: string };
    errorWithDigest.digest = 'test-digest-123';
    
    render(<ErrorBoundary error={errorWithDigest} reset={mockReset} />);
    
    expect(screen.getByText('오류 ID: test-digest-123')).toBeInTheDocument();
  });

  it('displays fallback error ID when digest is not available', () => {
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('오류 ID: N/A')).toBeInTheDocument();
  });

  it('logs error to console', () => {
    render(<ErrorBoundary error={mockError} reset={mockReset} />);
    
    expect(mockConsoleError).toHaveBeenCalledWith('Application Error:', mockError);
  });
});
