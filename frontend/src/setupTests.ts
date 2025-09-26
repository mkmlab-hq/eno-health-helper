import '@testing-library/jest-dom';

// Jest 환경 설정
Object.defineProperty(process.env, 'NODE_ENV', {
  writable: true,
  value: 'test'
});
