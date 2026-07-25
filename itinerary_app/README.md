# 상하이 여행 일정 관리 앱

Firebase 기반 웹 일정 관리 앱입니다. 관광지와 맛집을 자유롭게 추가/삭제하고 구글맵 링크를 저장할 수 있습니다.

## 🚀 빠른 시작

### 1️⃣ Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com)에서 새 프로젝트 생성
2. **Firestore Database** 생성 (위치: asia-southeast1, 룰스: 테스트 모드)
3. **Authentication** → Sign-in method → Anonymous 활성화
4. **프로젝트 설정** → 웹 앱 등록
5. Firebase config 복사

### 2️⃣ 환경 변수 설정

`.env` 파일 생성 (`.env.example` 참고):

```
REACT_APP_FIREBASE_API_KEY=xxx
REACT_APP_FIREBASE_AUTH_DOMAIN=xxx
REACT_APP_FIREBASE_PROJECT_ID=xxx
REACT_APP_FIREBASE_STORAGE_BUCKET=xxx
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=xxx
REACT_APP_FIREBASE_APP_ID=xxx
```

### 3️⃣ 로컬 실행

```bash
npm install
npm start
```

### 4️⃣ Vercel 배포

1. [Vercel](https://vercel.com/new)에서 이 repo 연결
2. 환경 변수 추가 (`.env` 값)
3. Deploy!

배포 후 링크: `https://your-project.vercel.app`

## 📝 사용법

- **관광지 추가**: 이름, 카테고리(도보/디디 몇분), 입장료, 메모, 구글맵 링크
- **맛집 추가**: 이름, 음식 종류, 위치, 가격, 메모, 구글맵 링크
- **삭제**: 각 항목의 쓰레기통 버튼 클릭

## 🛠 기술 스택

- React + TypeScript
- Firebase (Firestore + Auth)
- Tailwind CSS
- react-scripts (빌드)

## 📱 반응형 디자인

데스크톱/태블릿/모바일 모두 지원합니다.
