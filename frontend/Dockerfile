# Node.js 18 LTS 이미지 사용
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 (curl for healthcheck)
RUN apk add --no-cache curl

# package.json 및 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci --only=production

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 헬스체크를 위한 curl 설치 확인
RUN curl --version

# 개발 모드로 실행
CMD ["npm", "run", "dev"] 