# 🐳 Eno Health Helper - Docker 배포 가이드 (아카이브됨)

## ⚠️ 주의사항

**이 문서는 아카이브되었습니다.**  
프로젝트 크로노스 v2.2에서는 Docker 대신 Railway + Replicate 아키텍처를 사용합니다.  
최신 배포 가이드는 `PROJECT_CHRONOS_TECHNICAL_IMPLEMENTATION_V2_2.md`를 참조하세요.

## 📋 개요 (레거시)

이 가이드는 `eno-health-helper` 프로젝트의 레거시 Docker 배포 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 로컬 도커 이미지 빌드

```bash
# 백엔드 이미지 빌드
docker build -t eno-backend:latest ./backend

# 프론트엔드 이미지 빌드
docker build -t eno-frontend:latest ./frontend

# Functions 이미지 빌드
docker build -t eno-functions:latest ./functions
```

### 2. Docker Compose로 로컬 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 🔧 상세 설정

### 환경 변수

#### 백엔드 (.env)
```env
NODE_ENV=production
PORT=8000
DATABASE_URL=your_database_url
API_KEY=your_api_key
```

#### 프론트엔드 (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Eno Health Helper
```

#### Functions (.env)
```env
NODE_ENV=production
PORT=5001
FIREBASE_PROJECT_ID=your_project_id
```

### 포트 설정

- **백엔드**: 8000
- **프론트엔드**: 3000
- **Functions**: 5001

## 🚀 프로덕션 배포

### 1. GitHub Container Registry (GHCR) 푸시

```bash
# GHCR 로그인
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 이미지 태깅
docker tag eno-backend:latest ghcr.io/USERNAME/eno-health-helper/backend:latest
docker tag eno-frontend:latest ghcr.io/USERNAME/eno-health-helper/frontend:latest
docker tag eno-functions:latest ghcr.io/USERNAME/eno-health-helper/functions:latest

# 이미지 푸시
docker push ghcr.io/USERNAME/eno-health-helper/backend:latest
docker push ghcr.io/USERNAME/eno-health-helper/frontend:latest
docker push ghcr.io/USERNAME/eno-health-helper/functions:latest
```

### 2. Kubernetes 배포

```bash
# 배포 매니페스트 적용
kubectl apply -f k8s/deployment.yaml

# 서비스 상태 확인
kubectl get pods
kubectl get services
kubectl get deployments
```

### 3. Docker Swarm 배포

```bash
# 스택 배포
docker stack deploy -c docker-compose.prod.yml eno-health

# 서비스 상태 확인
docker service ls
docker service ps eno-health_backend
```

## 📊 모니터링 및 로그

### 로그 확인

```bash
# 컨테이너 로그
docker logs <container_id>

# Docker Compose 로그
docker-compose logs -f [service_name]

# Kubernetes 로그
kubectl logs -f deployment/eno-backend
```

### 헬스체크

```bash
# 백엔드 헬스체크
curl http://localhost:8000/health

# 프론트엔드 상태 확인
curl http://localhost:3000/api/health
```

## 🔍 문제 해결

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 사용 중인 포트 확인
   netstat -tulpn | grep :8000
   
   # 컨테이너 중지
   docker stop <container_id>
   ```

2. **이미지 빌드 실패**
   ```bash
   # 캐시 없이 빌드
   docker build --no-cache -t eno-backend:latest ./backend
   ```

3. **의존성 문제**
   ```bash
   # node_modules 삭제 후 재설치
   rm -rf node_modules package-lock.json
   npm install
   ```

### 디버깅

```bash
# 컨테이너 내부 접속
docker exec -it <container_id> /bin/bash

# 실행 중인 컨테이너 확인
docker ps -a

# 이미지 정보 확인
docker inspect <image_name>
```

## 📈 성능 최적화

### 멀티 스테이지 빌드

```dockerfile
# 예시: 프론트엔드 최적화
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 이미지 크기 최적화

```bash
# 불필요한 파일 제거
docker run --rm -v $(pwd):/app alpine:latest sh -c "cd /app && rm -rf node_modules"

# 멀티 아키텍처 빌드
docker buildx build --platform linux/amd64,linux/arm64 -t eno-backend:latest ./backend
```

## 🔐 보안 고려사항

1. **시크릿 관리**
   - 환경 변수는 `.env` 파일에 저장하지 않음
   - Kubernetes Secrets 또는 Docker Secrets 사용

2. **이미지 스캔**
   ```bash
   # Trivy로 취약점 스캔
   trivy image eno-backend:latest
   ```

3. **최소 권한 원칙**
   - 루트 사용자로 실행하지 않음
   - 필요한 포트만 노출

## 📚 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Kubernetes 문서](https://kubernetes.io/docs/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 🆘 지원

문제가 발생하거나 추가 도움이 필요한 경우:

1. GitHub Issues에 문제 보고
2. 프로젝트 문서 확인
3. 팀원과 상의

---

**마지막 업데이트**: 2025년 1월 27일
**버전**: 1.0.0
