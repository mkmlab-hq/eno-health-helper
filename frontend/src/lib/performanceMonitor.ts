export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: Date;
  category: 'navigation' | 'resource' | 'user-interaction' | 'api-call';
  metadata?: Record<string, any>;
}

export interface PerformanceReport {
  pageLoadTime: number;
  apiResponseTimes: number[];
  userInteractionTimes: number[];
  resourceLoadTimes: number[];
  averageApiResponseTime: number;
  averageUserInteractionTime: number;
  averageResourceLoadTime: number;
  totalMetrics: number;
}

class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetric[] = [];
  private observers: Map<string, PerformanceObserver> = new Map();

  private constructor() {
    this.initializeObservers();
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  private initializeObservers(): void {
    // 페이지 로드 성능 모니터링
    if (typeof window !== 'undefined') {
      this.observePageLoad();
      this.observeResourceLoading();
      this.observeUserInteractions();
    }
  }

  private observePageLoad(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.entryType === 'navigation') {
              const navEntry = entry as PerformanceNavigationTiming;
              this.recordMetric({
                name: 'page-load',
                value: navEntry.loadEventEnd - navEntry.loadEventStart,
                unit: 'ms',
                timestamp: new Date(),
                category: 'navigation',
                metadata: {
                  domContentLoaded: navEntry.domContentLoadedEventEnd - navEntry.domContentLoadedEventStart,
                  firstPaint: navEntry.loadEventEnd - navEntry.loadEventStart,
                  totalLoadTime: navEntry.loadEventEnd - navEntry.fetchStart
                }
              });
            }
          });
        });

        observer.observe({ entryTypes: ['navigation'] });
        this.observers.set('navigation', observer);
      } catch (error) {
        console.warn('페이지 로드 성능 모니터링 초기화 실패:', error);
      }
    }
  }

  private observeResourceLoading(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.entryType === 'resource') {
              const resourceEntry = entry as PerformanceResourceTiming;
              this.recordMetric({
                name: 'resource-load',
                value: resourceEntry.responseEnd - resourceEntry.requestStart,
                unit: 'ms',
                timestamp: new Date(),
                category: 'resource',
                metadata: {
                  resourceName: resourceEntry.name,
                  resourceType: resourceEntry.initiatorType,
                  transferSize: resourceEntry.transferSize
                }
              });
            }
          });
        });

        observer.observe({ entryTypes: ['resource'] });
        this.observers.set('resource', observer);
      } catch (error) {
        console.warn('리소스 로딩 성능 모니터링 초기화 실패:', error);
      }
    }
  }

  private observeUserInteractions(): void {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (entry.entryType === 'measure') {
              this.recordMetric({
                name: entry.name,
                value: entry.duration,
                unit: 'ms',
                timestamp: new Date(),
                category: 'user-interaction'
              });
            }
          });
        });

        observer.observe({ entryTypes: ['measure'] });
        this.observers.set('measure', observer);
      } catch (error) {
        console.warn('사용자 상호작용 성능 모니터링 초기화 실패:', error);
      }
    }
  }

  public recordMetric(metric: PerformanceMetric): void {
    this.metrics.push(metric);
    
    // 메트릭이 너무 많아지면 오래된 것 제거
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-500);
    }

    // 콘솔에 중요한 메트릭 로깅
    if (metric.value > 1000) { // 1초 이상 걸리는 작업
      console.warn(`🚨 성능 이슈 감지: ${metric.name} - ${metric.value}${metric.unit}`, metric.metadata);
    }
  }

  public measureUserInteraction(name: string, callback: () => void): void {
    const startTime = performance.now();
    
    try {
      callback();
    } finally {
      const endTime = performance.now();
      this.recordMetric({
        name: `user-interaction-${name}`,
        value: endTime - startTime,
        unit: 'ms',
        timestamp: new Date(),
        category: 'user-interaction'
      });
    }
  }

  public async measureApiCall<T>(name: string, apiCall: () => Promise<T>): Promise<T> {
    const startTime = performance.now();
    
    try {
      const result = await apiCall();
      const endTime = performance.now();
      
      this.recordMetric({
        name: `api-call-${name}`,
        value: endTime - startTime,
        unit: 'ms',
        timestamp: new Date(),
        category: 'api-call'
      });
      
      return result;
    } catch (error) {
      const endTime = performance.now();
      
      this.recordMetric({
        name: `api-call-${name}-error`,
        value: endTime - startTime,
        unit: 'ms',
        timestamp: new Date(),
        category: 'api-call',
        metadata: { error: error instanceof Error ? error.message : 'Unknown error' }
      });
      
      throw error;
    }
  }

  public getPerformanceReport(): PerformanceReport {
    const apiCalls = this.metrics.filter(m => m.category === 'api-call');
    const userInteractions = this.metrics.filter(m => m.category === 'user-interaction');
    const resourceLoads = this.metrics.filter(m => m.category === 'resource');
    const pageLoads = this.metrics.filter(m => m.name === 'page-load');

    const pageLoadTime = pageLoads.length > 0 ? pageLoads[0].value : 0;
    const apiResponseTimes = apiCalls.map(m => m.value);
    const userInteractionTimes = userInteractions.map(m => m.value);
    const resourceLoadTimes = resourceLoads.map(m => m.value);

    return {
      pageLoadTime,
      apiResponseTimes,
      userInteractionTimes,
      resourceLoadTimes,
      averageApiResponseTime: this.calculateAverage(apiResponseTimes),
      averageUserInteractionTime: this.calculateAverage(userInteractionTimes),
      averageResourceLoadTime: this.calculateAverage(resourceLoadTimes),
      totalMetrics: this.metrics.length
    };
  }

  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return Math.round((values.reduce((sum, val) => sum + val, 0) / values.length) * 100) / 100;
  }

  public getMetricsByCategory(category: PerformanceMetric['category']): PerformanceMetric[] {
    return this.metrics.filter(m => m.category === category);
  }

  public clearMetrics(): void {
    this.metrics = [];
  }

  public disconnect(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
  }
}

// 인스턴스 생성 및 export
export const performanceMonitor = PerformanceMonitor.getInstance();

export default PerformanceMonitor; 