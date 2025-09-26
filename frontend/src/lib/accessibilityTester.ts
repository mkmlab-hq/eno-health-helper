export interface AccessibilityIssue {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  element?: HTMLElement;
  selector?: string;
  impact: 'critical' | 'serious' | 'moderate' | 'minor';
  help: string;
  helpUrl?: string;
}

export interface AccessibilityReport {
  score: number;
  totalIssues: number;
  criticalIssues: number;
  seriousIssues: number;
  moderateIssues: number;
  minorIssues: number;
  issues: AccessibilityIssue[];
  timestamp: Date;
}

class AccessibilityTester {
  private static instance: AccessibilityTester;

  private constructor() {}

  public static getInstance(): AccessibilityTester {
    if (!AccessibilityTester.instance) {
      AccessibilityTester.instance = new AccessibilityTester();
    }
    return AccessibilityTester.instance;
  }

  public async runAccessibilityTest(): Promise<AccessibilityReport> {
    const issues: AccessibilityIssue[] = [];
    
    // 기본 접근성 테스트 실행
    issues.push(...this.testImages());
    issues.push(...this.testHeadings());
    issues.push(...this.testLinks());
    issues.push(...this.testForms());
    issues.push(...this.testColorContrast());
    issues.push(...this.testKeyboardNavigation());
    issues.push(...this.testScreenReaderSupport());

    // 점수 계산
    const score = this.calculateScore(issues);
    
    return {
      score,
      totalIssues: issues.length,
      criticalIssues: issues.filter(i => i.impact === 'critical').length,
      seriousIssues: issues.filter(i => i.impact === 'serious').length,
      moderateIssues: issues.filter(i => i.impact === 'moderate').length,
      minorIssues: issues.filter(i => i.impact === 'minor').length,
      issues,
      timestamp: new Date()
    };
  }

  private testImages(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    const images = document.querySelectorAll('img');

    images.forEach((img, index) => {
      if (!img.alt) {
        issues.push({
          id: `img-alt-${index}`,
          type: 'error',
          message: '이미지에 alt 속성이 없습니다.',
          element: img,
          selector: this.getElementSelector(img),
          impact: 'serious',
          help: '모든 이미지에는 alt 속성을 추가하여 스크린 리더 사용자가 이해할 수 있도록 해야 합니다.',
          helpUrl: 'https://www.w3.org/WAI/WCAG21/quickref/#text-alternatives'
        });
      }
    });

    return issues;
  }

  private testHeadings(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    
    if (headings.length === 0) {
      issues.push({
        id: 'no-headings',
        type: 'warning',
        message: '페이지에 제목(heading) 요소가 없습니다.',
        impact: 'moderate',
        help: '페이지 구조를 명확하게 하기 위해 제목 요소를 사용하는 것이 좋습니다.'
      });
    } else {
      // 제목 계층 구조 확인
      const headingLevels = Array.from(headings).map(h => parseInt(h.tagName.charAt(1)));
      let previousLevel = 0;
      
      headingLevels.forEach((level, index) => {
        if (level - previousLevel > 1) {
          issues.push({
            id: `heading-skip-${index}`,
            type: 'warning',
            message: `제목 계층이 건너뛰어졌습니다 (h${previousLevel} → h${level}).`,
            element: headings[index] as HTMLElement,
            selector: this.getElementSelector(headings[index] as HTMLElement),
            impact: 'moderate',
            help: '제목 계층을 순차적으로 사용하여 문서 구조를 명확하게 해야 합니다.'
          });
        }
        previousLevel = level;
      });
    }

    return issues;
  }

  private testLinks(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    const links = document.querySelectorAll('a');

    links.forEach((link, index) => {
      const text = link.textContent?.trim();
      const href = link.getAttribute('href');
      
      if (!text || text.length === 0) {
        issues.push({
          id: `link-no-text-${index}`,
          type: 'error',
          message: '링크에 텍스트가 없습니다.',
          element: link,
          selector: this.getElementSelector(link),
          impact: 'critical',
          help: '모든 링크에는 스크린 리더가 읽을 수 있는 텍스트가 있어야 합니다.'
        });
      }
      
      if (text === '여기' || text === '클릭' || text === '더보기') {
        issues.push({
          id: `link-generic-text-${index}`,
          type: 'warning',
          message: '링크 텍스트가 너무 일반적입니다.',
          element: link,
          selector: this.getElementSelector(link),
          impact: 'moderate',
          help: '링크의 목적을 명확하게 설명하는 텍스트를 사용해야 합니다.'
        });
      }
    });

    return issues;
  }

  private testForms(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    const forms = document.querySelectorAll('form');
    const inputs = document.querySelectorAll('input, textarea, select');

    inputs.forEach((input, index) => {
      const id = input.getAttribute('id');
      const label = document.querySelector(`label[for="${id}"]`);
      
      if (!id || !label) {
        issues.push({
          id: `form-no-label-${index}`,
          type: 'error',
          message: '폼 요소에 레이블이 없습니다.',
          element: input as HTMLElement,
          selector: this.getElementSelector(input as HTMLElement),
          impact: 'serious',
          help: '모든 폼 요소에는 연결된 레이블이 있어야 합니다.'
        });
      }
    });

    return issues;
  }

  private testColorContrast(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    
    // 간단한 색상 대비 테스트 (실제로는 더 정교한 알고리즘 필요)
    const textElements = document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6');
    
    textElements.forEach((element, index) => {
      const style = window.getComputedStyle(element);
      const color = style.color;
      const backgroundColor = style.backgroundColor;
      
      // 색상 대비가 너무 낮을 수 있는 경우 경고
      if (color === backgroundColor || color === 'transparent') {
        issues.push({
          id: `color-contrast-${index}`,
          type: 'warning',
          message: '텍스트와 배경색의 대비가 낮을 수 있습니다.',
          element: element as HTMLElement,
          selector: this.getElementSelector(element as HTMLElement),
          impact: 'moderate',
          help: '텍스트와 배경색의 대비를 높여 가독성을 개선해야 합니다.'
        });
      }
    });

    return issues;
  }

  private testKeyboardNavigation(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    const interactiveElements = document.querySelectorAll('button, a, input, textarea, select, [tabindex]');
    
    interactiveElements.forEach((element, index) => {
      const tabindex = element.getAttribute('tabindex');
      
      if (tabindex === '-1') {
        issues.push({
          id: `keyboard-tabindex-${index}`,
          type: 'warning',
          message: '요소가 키보드 탐색에서 제외되었습니다.',
          element: element as HTMLElement,
          selector: this.getElementSelector(element as HTMLElement),
          impact: 'moderate',
          help: '키보드 사용자도 모든 기능에 접근할 수 있어야 합니다.'
        });
      }
    });

    return issues;
  }

  private testScreenReaderSupport(): AccessibilityIssue[] {
    const issues: AccessibilityIssue[] = [];
    
    // ARIA 속성 확인
    const elementsWithAria = document.querySelectorAll('[aria-*]');
    
    elementsWithAria.forEach((element, index) => {
      const ariaLabel = element.getAttribute('aria-label');
      const ariaLabelledby = element.getAttribute('aria-labelledby');
      
      if (ariaLabel && ariaLabel.trim() === '') {
        issues.push({
          id: `aria-empty-label-${index}`,
          type: 'error',
          message: 'aria-label이 비어있습니다.',
          element: element as HTMLElement,
          selector: this.getElementSelector(element as HTMLElement),
          impact: 'serious',
          help: 'aria-label에는 의미 있는 텍스트가 있어야 합니다.'
        });
      }
    });

    return issues;
  }

  private getElementSelector(element: HTMLElement): string {
    if (element.id) {
      return `#${element.id}`;
    }
    if (element.className) {
      return `.${element.className.split(' ').join('.')}`;
    }
    return element.tagName.toLowerCase();
  }

  private calculateScore(issues: AccessibilityIssue[]): number {
    let totalScore = 100;
    
    issues.forEach(issue => {
      switch (issue.impact) {
        case 'critical':
          totalScore -= 10;
          break;
        case 'serious':
          totalScore -= 5;
          break;
        case 'moderate':
          totalScore -= 2;
          break;
        case 'minor':
          totalScore -= 1;
          break;
      }
    });
    
    return Math.max(0, totalScore);
  }
}

// 인스턴스 생성 및 export
export const accessibilityTester = AccessibilityTester.getInstance();

export default AccessibilityTester; 