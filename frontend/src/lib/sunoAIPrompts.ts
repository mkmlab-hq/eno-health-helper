// SunoAI 음악 생성 프롬프트
export const musicPrompts = {
  relaxation: "평화로운 자연 소리와 함께하는 이완 음악",
  meditation: "명상과 집중을 위한 차분한 음악",
  healing: "치유와 회복을 위한 따뜻한 음악",
  sleep: "수면을 돕는 부드러운 음악"
};

export const getMusicPrompt = (type: keyof typeof musicPrompts) => {
  return musicPrompts[type] || musicPrompts.relaxation;
};

// SunoAI 프롬프트 매퍼
export class SunoAIPromptMapper {
  private prompts: Record<string, string>;

  constructor() {
    this.prompts = {
      ...musicPrompts,
      // 추가 프롬프트들
      energy: "활력과 에너지를 불어넣는 동기부여 음악",
      focus: "집중력 향상을 위한 리듬감 있는 음악",
      creativity: "창의성 발현을 돕는 영감을 주는 음악",
      stress: "스트레스 해소를 위한 편안한 음악"
    };
  }

  getPrompt(type: string): string {
    return this.prompts[type] || this.prompts.relaxation;
  }

  getAllPrompts(): Record<string, string> {
    return { ...this.prompts };
  }

  addPrompt(type: string, prompt: string): void {
    this.prompts[type] = prompt;
  }

  // 감정에 따른 한국어 설명
  getEmotionKoreanDescription(emotion: string): string {
    const descriptions: Record<string, string> = {
      calm: "차분하고 평온한",
      excited: "신나고 활기찬",
      stressed: "스트레스 받은",
      happy: "행복하고 기쁜",
      sad: "슬프고 우울한",
      angry: "화가 난",
      anxious: "불안하고 긴장된",
      relaxed: "편안하고 여유로운"
    };
    return descriptions[emotion] || "일반적인";
  }

  // 감정에 따른 프롬프트 생성
  getPromptForEmotion(emotion: string): string {
    const emotionPrompts: Record<string, string> = {
      calm: "차분하고 평온한 분위기의 음악",
      excited: "신나고 활기찬 분위기의 음악",
      stressed: "스트레스 해소를 돕는 편안한 음악",
      happy: "행복하고 기쁜 감정을 표현하는 음악",
      sad: "슬픔을 위로하는 따뜻한 음악",
      angry: "분노를 진정시키는 차분한 음악",
      anxious: "불안을 해소하는 편안한 음악",
      relaxed: "편안함을 더하는 여유로운 음악"
    };
    return emotionPrompts[emotion] || "일반적인 음악";
  }

  // 최적화된 프롬프트 생성
  generateOptimizedPrompt(emotion: string, intensity: number): string {
    const basePrompt = this.getPromptForEmotion(emotion);
    const intensityModifier = intensity > 0.7 ? "강렬한" : intensity > 0.4 ? "적당한" : "부드러운";
    
    return `${intensityModifier} ${basePrompt}`;
  }
} 