# Google Cloud Storage 데이터 로더 설정 가이드

## 📋 개요

이 가이드는 구글 클라우드 스토리지(GCS)에 저장된 RPPG 및 음성 데이터를 eno-health-helper 프로젝트로 가져오는 방법을 설명합니다.

## 🔧 사전 요구사항

### 1. Google Cloud SDK 설치
```bash
# Windows (PowerShell)
winget install Google.CloudSDK

# 또는 수동 설치
# https://cloud.google.com/sdk/docs/install
```

### 2. Python 라이브러리 설치
```bash
pip install google-cloud-storage google-auth
```

### 3. Google Cloud 인증
```bash
# 기본 인증 설정
gcloud auth application-default login

# 또는 서비스 계정 키 파일 사용
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

## ⚙️ 환경 변수 설정

### Windows (PowerShell)
```powershell
$env:GOOGLE_CLOUD_PROJECT="your-project-id"
$env:GCS_BUCKET_NAME="your-bucket-name"
```

### Linux/Mac
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCS_BUCKET_NAME="your-bucket-name"
```

### .env 파일 사용 (권장)
```bash
# .env 파일 생성
echo "GOOGLE_CLOUD_PROJECT=your-project-id" > .env
echo "GCS_BUCKET_NAME=your-bucket-name" >> .env
```

## 🚀 데이터 다운로드 실행

### 1. 스크립트 실행
```bash
cd eno-health-helper/backend
python scripts/gcs_data_loader.py
```

### 2. 수동 실행 (Python)
```python
from scripts.gcs_data_loader import GCSDataLoader

# 로더 초기화
loader = GCSDataLoader(
    project_id="your-project-id",
    bucket_name="your-bucket-name"
)

# 인증 및 연결
loader.authenticate()
loader.connect_to_bucket()

# 데이터 다운로드
rppg_files = loader.download_rppg_data()
voice_files = loader.download_voice_data()

# 결과 확인
summary = loader.get_data_summary()
print(summary)
```

## 📁 데이터 구조

### GCS 버킷 구조 (권장)
```
your-bucket/
├── rppg/
│   ├── sample_001.mp4
│   ├── sample_002.mp4
│   └── metadata.json
├── voice/
│   ├── sample_001.wav
│   ├── sample_002.wav
│   └── metadata.json
└── shared/
    └── config.json
```

### 로컬 저장 구조
```
eno-health-helper/backend/
├── data/
│   ├── rppg/
│   │   ├── sample_001.mp4
│   │   └── sample_002.mp4
│   └── voice/
│       ├── sample_001.wav
│       └── sample_002.wav
└── scripts/
    └── gcs_data_loader.py
```

## 🔍 데이터 확인

### 1. 다운로드된 파일 확인
```bash
# RPPG 데이터
ls data/rppg/

# 음성 데이터
ls data/voice/
```

### 2. 파일 크기 및 정보 확인
```bash
# Windows
Get-ChildItem data -Recurse | Select-Object Name, Length, LastWriteTime

# Linux/Mac
find data -type f -exec ls -lh {} \;
```

## 🚨 문제 해결

### 인증 오류
```bash
# 기본 인증 재설정
gcloud auth application-default login

# 서비스 계정 키 확인
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### 버킷 접근 오류
```bash
# 버킷 권한 확인
gsutil ls gs://your-bucket-name

# IAM 권한 확인
gcloud projects get-iam-policy your-project-id
```

### 파일 다운로드 오류
```bash
# 네트워크 연결 확인
ping storage.googleapis.com

# GCS 연결 테스트
gsutil ls gs://your-bucket-name/
```

## 📊 데이터 사용 예시

### RPPG 데이터 로드
```python
import cv2
from pathlib import Path

# RPPG 비디오 파일 로드
video_path = Path("data/rppg/sample_001.mp4")
cap = cv2.VideoCapture(str(video_path))

frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)

cap.release()
print(f"로드된 프레임 수: {len(frames)}")
```

### 음성 데이터 로드
```python
import librosa
from pathlib import Path

# 음성 파일 로드
audio_path = Path("data/voice/sample_001.wav")
audio, sr = librosa.load(str(audio_path), sr=22050)

print(f"오디오 길이: {len(audio) / sr:.2f}초")
print(f"샘플 레이트: {sr}Hz")
```

## 🔐 보안 주의사항

1. **서비스 계정 키 파일을 Git에 커밋하지 마세요**
2. **환경 변수에 민감한 정보를 직접 입력하지 마세요**
3. **프로덕션 환경에서는 IAM 역할 기반 인증을 사용하세요**

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. Google Cloud Console에서 API 활성화 상태
2. 서비스 계정 권한 설정
3. 네트워크 연결 및 방화벽 설정
4. Python 라이브러리 버전 호환성

## 📚 추가 자료

- [Google Cloud Storage 문서](https://cloud.google.com/storage/docs)
- [Google Cloud Python 클라이언트](https://googleapis.dev/python/storage/latest/index.html)
- [Google Cloud 인증 가이드](https://cloud.google.com/docs/authentication) 