'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface HealthData {
  rppg?: {
    heartRate: number;
    stressIndex: number;
    confidence: number;
    quality: string;
  };
  voice?: {
    pitch: number;
    clarity: number;
    emotion: string;
    quality: string;
  };
  fusion?: {
    digitalTemperament: string;
    overallScore: number;
    recommendations: string[];
  };
}

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

interface AIChatProps {
  healthData: HealthData;
  maxQuestions?: number;
  onClose?: () => void;
}

export default function AIChat({ healthData, maxQuestions = 10, onClose }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: `안녕하세요! 🩺 엔오 건강 도우미 AI입니다.

현재 건강 측정 결과를 분석해보니:
${healthData.rppg ? `💓 심혈관: 심박수 ${healthData.rppg.heartRate} BPM, 스트레스 ${(healthData.rppg.stressIndex * 100).toFixed(1)}%` : ''}
${healthData.voice ? `🎤 음성: 피치 ${healthData.voice.pitch} Hz, 명확도 ${(healthData.voice.clarity * 100).toFixed(1)}%` : ''}
${healthData.fusion ? `🧠 체질: ${healthData.fusion.digitalTemperament}, 종합 점수 ${healthData.fusion.overallScore}/100` : ''}

건강에 대해 궁금한 점이 있으시면 언제든 물어보세요! (무료 질문 ${maxQuestions}회 가능)`,
      timestamp: new Date()
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [remainingQuestions, setRemainingQuestions] = useState(maxQuestions);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading || remainingQuestions <= 0) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setQuestionCount(prev => prev + 1);
    setRemainingQuestions(prev => prev - 1);

    try {
      // Firebase Functions를 통한 AI 응답 요청
      const response = await fetch('/api/ai-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          healthData,
          questionCount: questionCount + 1
        }),
      });

      if (!response.ok) {
        throw new Error('AI 응답 생성 실패');
      }

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('AI 채팅 오류:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: '죄송합니다. AI 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-2xl w-full max-w-2xl h-[600px] flex flex-col shadow-2xl border border-cyan-500/30"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-cyan-500/30">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-xl">🤖</span>
            </div>
            <div>
              <h3 className="text-white font-semibold">엔오 AI 건강 상담사</h3>
              <p className="text-cyan-400 text-sm">무료 질문 {remainingQuestions}회 남음</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                      : 'bg-gray-800 text-gray-100 border border-cyan-500/30'
                  }`}
                >
                  <p className="whitespace-pre-line text-sm">{message.content}</p>
                  <p className={`text-xs mt-2 ${
                    message.type === 'user' ? 'text-cyan-100' : 'text-gray-400'
                  }`}>
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-gray-800 rounded-2xl px-4 py-3 border border-cyan-500/30">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-cyan-400 text-sm">AI가 답변을 생성하고 있습니다...</span>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-cyan-500/30">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={remainingQuestions > 0 ? "건강에 대해 궁금한 점을 물어보세요..." : "무료 질문을 모두 사용했습니다"}
              disabled={isLoading || remainingQuestions <= 0}
              className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 border border-cyan-500/30 focus:border-cyan-400 focus:outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading || remainingQuestions <= 0}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-6 py-3 rounded-xl hover:from-cyan-600 hover:to-blue-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '전송 중...' : '전송'}
            </button>
          </form>
          
          {remainingQuestions <= 0 && (
            <div className="mt-3 p-3 bg-yellow-900/30 border border-yellow-500/50 rounded-lg">
              <p className="text-yellow-400 text-sm text-center">
                🎯 무료 질문을 모두 사용했습니다. 프리미엄 서비스로 업그레이드하여 더 많은 질문을 할 수 있습니다.
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
