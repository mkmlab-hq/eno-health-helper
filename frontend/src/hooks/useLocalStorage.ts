import { useState, useEffect, useCallback } from 'react';

export interface UseLocalStorageOptions<T> {
  defaultValue: T;
  key: string;
  serialize?: (value: T) => string;
  deserialize?: (value: string) => T;
}

export function useLocalStorage<T>(
  options: UseLocalStorageOptions<T>
) {
  const {
    defaultValue,
    key,
    serialize = JSON.stringify,
    deserialize = JSON.parse,
  } = options;

  // 초기값을 가져오는 함수
  const getInitialValue = (): T => {
    if (typeof window === 'undefined') {
      return defaultValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? deserialize(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  };

  const [storedValue, setStoredValue] = useState<T>(getInitialValue);

  // 로컬 스토리지에 값을 저장하는 함수
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, serialize(valueToStore));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, serialize, storedValue]);

  // 로컬 스토리지에서 값을 제거하는 함수
  const removeValue = useCallback(() => {
    try {
      setStoredValue(defaultValue);
      
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, defaultValue]);

  // 로컬 스토리지 값이 변경되었는지 확인하는 함수
  const hasValue = useCallback(() => {
    if (typeof window === 'undefined') {
      return false;
    }

    try {
      return window.localStorage.getItem(key) !== null;
    } catch (error) {
      console.warn(`Error checking localStorage key "${key}":`, error);
      return false;
    }
  }, [key]);

  // 로컬 스토리지 값의 크기를 확인하는 함수
  const getSize = useCallback(() => {
    if (typeof window === 'undefined') {
      return 0;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? new Blob([item]).size : 0;
    } catch (error) {
      console.warn(`Error getting localStorage size for key "${key}":`, error);
      return 0;
    }
  }, [key]);

  // 다른 탭에서 로컬 스토리지 변경을 감지
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(deserialize(e.newValue));
        } catch (error) {
          console.warn(`Error deserializing localStorage value for key "${key}":`, error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, deserialize]);

  return {
    value: storedValue,
    setValue,
    removeValue,
    hasValue: hasValue(),
    size: getSize(),
    key,
  };
}

// 특정 용도별 훅들
export function useUserPreferences() {
  return useLocalStorage({
    key: 'eno-health-user-preferences',
    defaultValue: {
      theme: 'system' as 'light' | 'dark' | 'system',
      language: 'ko',
      notifications: true,
      autoSave: true,
      measurementDuration: 35,
    },
  });
}

export function useMeasurementHistory() {
  return useLocalStorage({
    key: 'eno-health-measurement-history',
    defaultValue: [] as Array<{
      id: string;
      timestamp: number;
      type: 'rppg' | 'voice' | 'combined';
      results: any;
    }>,
  });
}

export function useAppSettings() {
  return useLocalStorage({
    key: 'eno-health-app-settings',
    defaultValue: {
      version: '1.0.0',
      lastUpdated: Date.now(),
      features: {
        rppg: true,
        voice: true,
        dashboard: true,
        export: true,
      },
    },
  });
}
