# 🌐 mkmlab.space 도메인 연결 가이드

## 📋 사전 준비사항

### **1. 도메인 소유권 확인**
- [ ] `mkmlab.space` 도메인을 소유하고 있음
- [ ] 도메인 관리자 권한 보유
- [ ] DNS 설정 권한 보유

### **2. Firebase 프로젝트 설정**
- [ ] Firebase 프로젝트 생성 완료
- [ ] Firebase CLI 설치 및 로그인 완료
- [ ] 프로젝트 ID 확인

---

## 🚀 1단계: Firebase Hosting 배포

### **1-1: 프로덕션 빌드**
```bash
cd frontend
npm run build
```

### **1-2: Firebase 배포**
```bash
cd ..
firebase deploy --only hosting
```

### **1-3: 배포 확인**
- 기본 URL: `https://[PROJECT_ID].web.app`
- 예시: `https://eno-health-helper.web.app`

---

## 🔗 2단계: 커스텀 도메인 연결

### **2-1: Firebase Console 접속**
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. 프로젝트 선택 (`eno-health-helper`)
3. 왼쪽 메뉴에서 **Hosting** 클릭

### **2-2: 커스텀 도메인 추가**
1. **Custom domains** 탭 클릭
2. **Add custom domain** 버튼 클릭
3. 도메인 입력: `mkmlab.space`
4. **Continue** 클릭

### **2-3: 도메인 소유권 확인**
1. **TXT record** 추가 안내 확인
2. DNS 제공업체에서 TXT 레코드 추가
3. **Verify** 버튼 클릭

---

## 📝 3단계: DNS 설정

### **3-1: TXT 레코드 추가 (도메인 소유권 확인용)**
```
Type: TXT
Name: @
Value: [Firebase에서 제공하는 TXT 값]
TTL: 3600 (또는 기본값)
```

### **3-2: A 레코드 추가 (도메인 연결용)**
```
Type: A
Name: @
Value: 151.101.1.195
TTL: 3600 (또는 기본값)
```

### **3-3: CNAME 레코드 추가 (www 서브도메인용)**
```
Type: CNAME
Name: www
Value: [PROJECT_ID].web.app
TTL: 3600 (또는 기본값)
```

---

## ⏳ 4단계: SSL 인증서 발급 대기

### **4-1: 자동 SSL 발급**
- Firebase가 자동으로 SSL 인증서 발급
- 일반적으로 **24-48시간** 소요
- 도메인 연결 완료 후 `https://mkmlab.space` 접근 가능

### **4-2: SSL 상태 확인**
- Firebase Console > Hosting > Custom domains
- SSL 인증서 상태: **Active** 표시 확인

---

## 🧪 5단계: 테스트 및 검증

### **5-1: 도메인 접근 테스트**
```bash
# 메인 페이지
curl -I https://mkmlab.space

# 랜딩페이지
curl -I https://mkmlab.space/landing

# 기존 앱
curl -I https://mkmlab.space/measure
```

### **5-2: 브라우저에서 확인**
- [ ] `https://mkmlab.space` 접근 가능
- [ ] `https://mkmlab.space/landing` 랜딩페이지 표시
- [ ] `https://mkmlab.space/measure` 기존 앱 작동
- [ ] SSL 인증서 정상 작동 (🔒 표시)

---

## 🔧 6단계: 추가 최적화

### **6-1: 리다이렉트 설정 (선택사항)**
```json
// firebase.json
{
  "hosting": {
    "redirects": [
      {
        "source": "/",
        "destination": "/landing",
        "type": 301
      }
    ]
  }
}
```

### **6-2: 캐싱 최적화**
```json
// firebase.json
{
  "hosting": {
    "headers": [
      {
        "source": "**/*.@(js|css|png|jpg|jpeg|gif|svg)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      }
    ]
  }
}
```

---

## 🚨 문제 해결

### **문제 1: 도메인 소유권 확인 실패**
- **원인**: TXT 레코드가 아직 전파되지 않음
- **해결**: 24-48시간 대기 후 재시도

### **문제 2: SSL 인증서 발급 실패**
- **원인**: DNS 설정 오류
- **해결**: A 레코드와 CNAME 레코드 재확인

### **문제 3: 페이지 로딩 실패**
- **원인**: Firebase Hosting 설정 오류
- **해결**: `firebase.json` 설정 재확인

---

## 📞 지원 및 문의

### **Firebase 지원**
- [Firebase 문서](https://firebase.google.com/docs/hosting/custom-domain)
- [Firebase 커뮤니티](https://firebase.community/)

### **DNS 설정 지원**
- 도메인 제공업체별 DNS 설정 가이드 참조
- 일반적으로 **A 레코드**와 **CNAME 레코드** 설정

---

## 🎯 최종 목표

**성공적으로 연결되면:**
- ✅ `https://mkmlab.space` → 메인 페이지
- ✅ `https://mkmlab.space/landing` → 랜딩페이지
- ✅ `https://mkmlab.space/measure` → 건강 측정 앱
- ✅ 모든 페이지에서 SSL 인증서 정상 작동
- ✅ 글로벌 CDN을 통한 빠른 로딩

**이제 mkmlab.space로 브랜드가 통일된 완벽한 웹사이트가 완성됩니다!** 🚀
