# Firebase Functions Dockerfile
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# Install Firebase CLI globally
RUN npm install -g firebase-tools

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 5001

# 환경 변수 설정
ENV NODE_ENV=development
ENV PORT=5001

# Start Firebase Functions emulator
CMD ["firebase", "emulators:start", "--only", "functions", "--port", "5001"] 