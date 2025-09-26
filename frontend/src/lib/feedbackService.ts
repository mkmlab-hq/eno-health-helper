export interface FeedbackData {
  rating: number;
  comment: string;
  category: 'general' | 'rppg' | 'voice' | 'music' | 'ui';
  timestamp: Date;
  userId?: string;
  sessionId?: string;
}

export interface FeedbackResponse {
  success: boolean;
  message: string;
  feedbackId?: string;
}

class FeedbackService {
  private static instance: FeedbackService;
  private feedbackStorage: FeedbackData[] = [];
  private sessionId: string;

  private constructor() {
    this.sessionId = this.generateSessionId();
    this.loadFromLocalStorage();
  }

  public static getInstance(): FeedbackService {
    if (!FeedbackService.instance) {
      FeedbackService.instance = new FeedbackService();
    }
    return FeedbackService.instance;
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private loadFromLocalStorage(): void {
    try {
      const stored = localStorage.getItem('eno-health-feedback');
      if (stored) {
        this.feedbackStorage = JSON.parse(stored).map((item: any) => ({
          ...item,
          timestamp: new Date(item.timestamp)
        }));
      }
    } catch (error) {
      console.warn('로컬 스토리지에서 피드백 로드 실패:', error);
    }
  }

  private saveToLocalStorage(): void {
    try {
      localStorage.setItem('eno-health-feedback', JSON.stringify(this.feedbackStorage));
    } catch (error) {
      console.warn('로컬 스토리지에 피드백 저장 실패:', error);
    }
  }

  public async submitFeedback(feedback: FeedbackData): Promise<FeedbackResponse> {
    try {
      // 세션 ID 추가
      const enrichedFeedback: FeedbackData = {
        ...feedback,
        sessionId: this.sessionId,
        timestamp: new Date()
      };

      // 로컬 스토리지에 저장
      this.feedbackStorage.push(enrichedFeedback);
      this.saveToLocalStorage();

      // Firebase에 저장 시도 (선택사항)
      try {
        await this.saveToFirebase(enrichedFeedback);
      } catch (firebaseError) {
        console.warn('Firebase 저장 실패, 로컬에만 저장됨:', firebaseError);
      }

      return {
        success: true,
        message: '피드백이 성공적으로 제출되었습니다.',
        feedbackId: enrichedFeedback.sessionId
      };

    } catch (error) {
      console.error('피드백 제출 실패:', error);
      return {
        success: false,
        message: '피드백 제출에 실패했습니다. 다시 시도해주세요.'
      };
    }
  }

  private async saveToFirebase(feedback: FeedbackData): Promise<void> {
    // Firebase 연동이 구현되면 여기에 추가
    // 현재는 로컬 스토리지만 사용
    return Promise.resolve();
  }

  public getFeedbackStats(): {
    totalCount: number;
    averageRating: number;
    categoryBreakdown: Record<string, number>;
    recentFeedback: FeedbackData[];
  } {
    const totalCount = this.feedbackStorage.length;
    const averageRating = totalCount > 0 
      ? this.feedbackStorage.reduce((sum, item) => sum + item.rating, 0) / totalCount
      : 0;

    const categoryBreakdown = this.feedbackStorage.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recentFeedback = [...this.feedbackStorage]
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 5);

    return {
      totalCount,
      averageRating: Math.round(averageRating * 10) / 10,
      categoryBreakdown,
      recentFeedback
    };
  }

  public getAllFeedback(): FeedbackData[] {
    return [...this.feedbackStorage];
  }

  public clearFeedback(): void {
    this.feedbackStorage = [];
    localStorage.removeItem('eno-health-feedback');
  }
}

export default FeedbackService; 