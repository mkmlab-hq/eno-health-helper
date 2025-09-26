'use client';

import { useState, useEffect } from 'react';

interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
}

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 간단한 사용자 시뮬레이션
    // 실제 구현에서는 Firebase Auth를 사용해야 함
    const mockUser: User = {
      uid: 'mock-user-123',
      email: 'user@example.com',
      displayName: '테스트 사용자'
    };
    
    setUser(mockUser);
    setLoading(false);
  }, []);

  return { user, loading };
};
