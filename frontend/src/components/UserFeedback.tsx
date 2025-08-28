'use client';

import React, { useState } from 'react';
import { StarIcon } from '@heroicons/react/24/solid';
import { StarIcon as StarOutlineIcon } from '@heroicons/react/24/outline';

interface FeedbackData {
  rating: number;
  comment: string;
  category: 'general' | 'rppg' | 'voice' | 'music' | 'ui';
  timestamp: Date;
}

interface UserFeedbackProps {
  onSubmit: (feedback: FeedbackData) => void;
  onClose: () => void;
}

const UserFeedback: React.FC<UserFeedbackProps> = ({ onSubmit, onClose }) => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [category, setCategory] = useState<'general' | 'rppg' | 'voice' | 'music' | 'ui'>('general');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) return;

    setIsSubmitting(true);
    
    const feedback: FeedbackData = {
      rating,
      comment,
      category,
      timestamp: new Date()
    };

    try {
      await onSubmit(feedback);
      // 폼 초기화
      setRating(0);
      setComment('');
      setCategory('general');
      onClose();
    } catch (error) {
      console.error('피드백 제출 실패:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const categories = [
    { value: 'general', label: '전체적인 경험' },
    { value: 'rppg', label: '심박수 측정' },
    { value: 'voice', label: '음성 분석' },
    { value: 'music', label: '음악 생성' },
    { value: 'ui', label: '사용자 인터페이스' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">사용자 피드백</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 카테고리 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              피드백 카테고리
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* 별점 평가 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              만족도 평가
            </label>
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className="text-2xl text-yellow-400 hover:text-yellow-500 transition-colors"
                >
                  {star <= rating ? (
                    <StarIcon className="w-8 h-8" />
                  ) : (
                    <StarOutlineIcon className="w-8 h-8" />
                  )}
                </button>
              ))}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {rating === 0 && '별점을 선택해주세요'}
              {rating === 1 && '매우 불만족'}
              {rating === 2 && '불만족'}
              {rating === 3 && '보통'}
              {rating === 4 && '만족'}
              {rating === 5 && '매우 만족'}
            </p>
          </div>

          {/* 코멘트 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              추가 의견 (선택사항)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="사용 경험이나 개선 제안을 자유롭게 작성해주세요..."
            />
          </div>

          {/* 제출 버튼 */}
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={rating === 0 || isSubmitting}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? '제출 중...' : '피드백 제출'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserFeedback; 