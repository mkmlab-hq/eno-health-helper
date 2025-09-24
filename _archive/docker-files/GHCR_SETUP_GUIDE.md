# 🔐 GitHub Container Registry (GHCR) 설정 가이드

## 📋 개요

이 가이드는 `eno-health-helper` 프로젝트의 도커 이미지를 GitHub Container Registry에 푸시하는 방법을 설명합니다.

## 🚀 1단계: GitHub Personal Access Token 생성

### 1.1 GitHub 설정 페이지 접속
1. GitHub.com에 로그인
2. 우측 상단 프로필 아이콘 클릭 → **Settings**
3. 좌측 메뉴에서 **Developer settings** 클릭
4. **Personal access tokens** → **Tokens (classic)** 클릭

### 1.2 새 토큰 생성
1. **Generate new token** → **Generate new token (classic)** 클릭
2. **Note**: `eno-health-helper-docker` 입력
3. **Expiration**: `No expiration` 또는 적절한 만료일 선택
4. **Scopes** 선택:
   - ✅ `write:packages` (패키지 쓰기 권한)
   - ✅ `read:packages` (패키지 읽기 권한)
   - ✅ `delete:packages` (패키지 삭제 권한, 선택사항)

### 1.3 토큰 저장
1. **Generate token** 클릭
2. **생성된 토큰을 안전한 곳에 복사하여 저장**
3. ⚠️ **중요**: 이 토큰은 다시 볼 수 없으므로 반드시 저장해두세요!

## 🔐 2단계: GitHub Container Registry 로그인

### 2.1 터미널에서 로그인
```bash
# PowerShell에서
echo $env:GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 또는 직접 입력
docker login ghcr.io -u YOUR_USERNAME -p YOUR_TOKEN
```

### 2.2 환경 변수 설정 (권장)
```powershell
# PowerShell에서
$env:GITHUB_TOKEN = "ghp_your_token_here"
$env:GITHUB_USERNAME = "your_username"

# 또는 .env 파일 생성
echo "GITHUB_TOKEN=ghp_your_token_here" > .env
echo "GITHUB_USERNAME=your_username" >> .env
```

## 🏷️ 3단계: 이미지 태깅

### 3.1 로컬 이미지 확인
```bash
docker images | Select-String "eno"
```

### 3.2 GHCR 형식으로 태깅
```bash
# 백엔드
docker tag eno-backend:latest ghcr.io/YOUR_USERNAME/eno-health-helper/backend:latest

# 프론트엔드
docker tag eno-frontend:latest ghcr.io/YOUR_USERNAME/eno-health-helper/frontend:latest

# Functions
docker tag eno-functions:latest ghcr.io/YOUR_USERNAME/eno-health-helper/functions:latest
```

## 📤 4단계: 이미지 푸시

### 4.1 개별 푸시
```bash
# 백엔드 푸시
docker push ghcr.io/YOUR_USERNAME/eno-health-helper/backend:latest

# 프론트엔드 푸시
docker push ghcr.io/YOUR_USERNAME/eno-health-helper/frontend:latest

# Functions 푸시
docker push ghcr.io/YOUR_USERNAME/eno-health-helper/functions:latest
```

### 4.2 자동화 스크립트 사용 (권장)
```powershell
# PowerShell에서
.\scripts\push-to-ghcr.ps1 -GitHubUsername "YOUR_USERNAME" -GitHubToken "YOUR_TOKEN" -Tag "latest"
```

## 🌐 5단계: 푸시된 이미지 확인

### 5.1 GitHub에서 확인
1. GitHub 레포지토리 페이지 접속
2. **Packages** 탭 클릭
3. 푸시된 도커 이미지들 확인

### 5.2 로컬에서 확인
```bash
docker images | Select-String "ghcr.io/YOUR_USERNAME/eno-health-helper"
```

## 🔍 6단계: 문제 해결

### 6.1 인증 오류
```bash
# 토큰 재설정
docker logout ghcr.io
docker login ghcr.io -u YOUR_USERNAME -p YOUR_TOKEN
```

### 6.2 권한 오류
- GitHub 토큰에 `write:packages` 권한이 있는지 확인
- 레포지토리에 대한 쓰기 권한이 있는지 확인

### 6.3 네트워크 오류
```bash
# Docker 데몬 재시작
# 또는 VPN/프록시 설정 확인
```

## 📚 7단계: 다음 단계

이미지 푸시가 완료되면:

1. **프로덕션 배포**: Kubernetes 또는 Docker Swarm으로 배포
2. **CI/CD 파이프라인**: GitHub Actions로 자동화
3. **모니터링**: 배포된 컨테이너 상태 모니터링

## 🆘 지원

문제가 발생하거나 추가 도움이 필요한 경우:

1. GitHub Issues에 문제 보고
2. GitHub Container Registry 문서 참조
3. Docker 공식 문서 참조

---

**마지막 업데이트**: 2025년 1월 27일  
**버전**: 1.0.0
