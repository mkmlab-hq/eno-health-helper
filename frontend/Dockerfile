# Node.js 18 Alpine 이미지 사용
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apk add --no-cache libc6-compat

# 패키지 파일 복사 및 의존성 설치
COPY package*.json ./

# husky prepare 스크립트 비활성화
RUN npm config set ignore-scripts true

# 의존성 설치
RUN npm ci

# 소스 코드 복사
COPY . .

# husky 재활성화 및 Next.js 앱 빌드 (ESLint 오류 무시)
RUN npm config set ignore-scripts false
RUN npm run build -- --no-lint

# 포트 3000 노출
EXPOSE 3000

# 환경 변수 설정
ENV NODE_ENV=production
ENV PORT=3000

# 애플리케이션 실행
CMD ["npm", "start"] 