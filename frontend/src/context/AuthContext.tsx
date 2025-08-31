'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
// 개발용 더미 AuthContext (Firebase 비활성화)
type User = { email: string } | null;
type UserCredential = { user: User };

// 더미 auth 객체 및 함수
const auth = {};
const signInWithEmailAndPassword = async (_auth: any, email: string, password: string) => {
  console.log('개발 모드: 로그인 시뮬레이션', { email, password });
  return { user: { email } };
};
const createUserWithEmailAndPassword = async (_auth: any, email: string, password: string) => {
  console.log('개발 모드: 회원가입 시뮬레이션', { email, password });
  return { user: { email } };
};
const signOut = async (_auth: any) => {
  console.log('개발 모드: 로그아웃 시뮬레이션');
  return;
};
const onAuthStateChanged = (_auth: any, callback: (user: User) => void) => {
  // 개발 모드: 항상 null 유저
  callback(null);
  return () => {};
};

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<UserCredential>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function signIn(email: string, password: string) {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  }

  async function signUp(email: string, password: string): Promise<UserCredential> {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      return userCredential;
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  }

  async function logout() {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }

  useEffect(() => {
    if (typeof onAuthStateChanged === 'function') {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        setCurrentUser(user);
        setLoading(false);
      });
      return unsubscribe;
    } else {
      // 개발 모드: 더미 유저 처리
      setCurrentUser(null);
      setLoading(false);
      return () => {};
    }
  }, []);

  const value: AuthContextType = {
    currentUser,
    loading,
    signIn,
    signUp,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
} 