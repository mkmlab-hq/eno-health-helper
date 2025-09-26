# Node.js 18 Alpine 이미지 사용
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 파일 복사 및 의존성 설치
COPY package*.json ./
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 포트 5001 노출 (Firebase Functions 기본 포트)
EXPOSE 5001

# 환경 변수 설정
ENV NODE_ENV=production
ENV PORT=5001

# 애플리케이션 실행
CMD ["npm", "start"] 