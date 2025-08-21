# 🚀 엔오건강도우미 빠른 시작 가이드

## 📋 **사전 요구사항**

- **Node.js**: 18.x 이상
- **Python**: 3.9 이상
- **Docker**: 20.x 이상 (선택사항)
- **Git**: 최신 버전

## 🎯 **빠른 시작 (로컬 개발)**

### **1단계: 프로젝트 클론 및 설정**

```bash
# 레포지토리 클론
git clone https://github.com/mkmlab-hq/eno-health-helper.git
cd eno-health-helper

# 의존성 설치
npm install --prefix frontend
pip install -r backend/requirements.txt
```

### **2단계: 환경 변수 설정**

```bash
# Frontend 환경 변수
cd frontend
cp .env.example .env.local

# Backend 환경 변수
cd ../backend
cp .env.example .env
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=엔오건강도우미
```

**Backend (.env):**
```bash
DATABASE_URL=postgresql://eno_user:eno_password@localhost/eno_health
SECRET_KEY=your-secret-key-here
MKM_CORE_AI_URL=http://localhost:8001
```

### **3단계: 데이터베이스 설정**

```bash
# PostgreSQL 설치 (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# 데이터베이스 생성
sudo -u postgres psql
CREATE DATABASE eno_health;
CREATE USER eno_user WITH PASSWORD 'eno_password';
GRANT ALL PRIVILEGES ON DATABASE eno_health TO eno_user;
\q
```

### **4단계: 서비스 실행**

```bash
# Backend 실행 (새 터미널)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend 실행 (새 터미널)
cd frontend
npm run dev
```

### **5단계: 접속 확인**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## 🐳 **빠른 시작 (Docker)**

### **1단계: Docker Compose 실행**

```bash
# 전체 서비스 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### **2단계: 서비스 상태 확인**

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f frontend
docker-compose logs -f backend
```

### **3단계: 접속 확인**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🔧 **개발 환경 설정**

### **Frontend 개발**

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 린트 검사
npm run lint

# 타입 체크
npm run type-check
```

### **Backend 개발**

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn main:app --reload

# 테스트 실행
pytest

# 코드 포맷팅
black .
isort .
```

## 📱 **주요 기능 테스트**

### **1. QR 코드 스캔 테스트**

```bash
# 테스트용 QR 코드 생성
echo "ENO_PRODUCT_001" | qrencode -o test_qr.png
```

### **2. RPPG 측정 테스트**

```bash
# 카메라 권한 테스트
curl -X POST http://localhost:8000/api/v1/health/test-camera
```

### **3. 음성 분석 테스트**

```bash
# 마이크 권한 테스트
curl -X POST http://localhost:8000/api/v1/health/test-audio
```

## 🚨 **문제 해결**

### **일반적인 문제들**

#### **Frontend 오류**
```bash
# Node 모듈 문제
rm -rf node_modules package-lock.json
npm install

# Next.js 캐시 문제
rm -rf .next
npm run dev
```

#### **Backend 오류**
```bash
# Python 가상환경 문제
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 데이터베이스 연결 문제
sudo systemctl restart postgresql
```

#### **Docker 오류**
```bash
# 컨테이너 정리
docker-compose down -v
docker system prune -a

# 이미지 재빌드
docker-compose build --no-cache
```

### **포트 충돌 해결**

```bash
# 포트 사용 확인
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# 프로세스 종료
kill -9 <PID>
```

## 📚 **다음 단계**

1. **API 개발**: `/api/v1/measure` 엔드포인트 구현
2. **데이터베이스 모델**: 사용자 및 측정 데이터 모델 설계
3. **의료어 필터**: 120개 의료 금지 용어 필터 구현
4. **면책 시스템**: 3계층 면책 UI 구현
5. **테스트 작성**: 단위 테스트 및 통합 테스트 작성

## 🤝 **도움 요청**

- **GitHub Issues**: [Issues](https://github.com/mkmlab-hq/eno-health-helper/issues)
- **문서**: [Wiki](https://github.com/mkmlab-hq/eno-health-helper/wiki)
- **토론**: [Discussions](https://github.com/mkmlab-hq/eno-health-helper/discussions)

---

**즐거운 개발 되세요! 🎉** 