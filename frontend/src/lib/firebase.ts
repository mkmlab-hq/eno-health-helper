import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInWithPopup, 
  GoogleAuthProvider, 
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User
} from 'firebase/auth';
import { 
  getFirestore, 
  doc, 
  setDoc, 
  getDoc, 
  collection, 
  addDoc,
  query,
  where,
  orderBy,
  limit,
  getDocs
} from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "eno-health-helper.firebaseapp.com",
  projectId: "eno-health-helper",
  storageBucket: "eno-health-helper.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456"
};

// Firebase 초기화
const app = initializeApp(firebaseConfig);

// 서비스 내보내기
export const auth = getAuth(app);
export const db = getFirestore(app);

// Google 로그인
export const signInWithGoogle = async () => {
  try {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(auth, provider);
    
    // 사용자 정보를 Firestore에 저장
    if (result.user) {
      await saveUserToFirestore(result.user);
    }
    
    return { success: true, user: result.user };
  } catch (error) {
    console.error('Google 로그인 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage };
  }
};

// 카카오 로그인 (Firebase Custom Token 사용)
export const signInWithKakao = async () => {
  try {
    // 카카오 SDK를 통한 로그인
    if (typeof window !== 'undefined' && window.Kakao) {
      const response = await new Promise((resolve, reject) => {
        window.Kakao.Auth.login({
          success: resolve,
          fail: reject
        });
      });
      
      // 카카오 사용자 정보 가져오기
      const userInfo = await new Promise<any>((resolve, reject) => {
        window.Kakao.API.request({
          url: '/v2/user/me',
          success: resolve,
          fail: reject
        });
      });
      
      // Firebase Custom Token으로 로그인 (백엔드에서 생성 필요)
      // 여기서는 시뮬레이션용으로 성공 응답
      const mockUser = {
        uid: `kakao_${userInfo.id}`,
        email: userInfo.kakao_account?.email || `${userInfo.id}@kakao.com`,
        displayName: userInfo.properties?.nickname || '카카오 사용자',
        photoURL: userInfo.properties?.profile_image || null
      };
      
      await saveUserToFirestore(mockUser);
      return { success: true, user: mockUser };
    }
    
    throw new Error('카카오 SDK를 찾을 수 없습니다.');
  } catch (error) {
    console.error('카카오 로그인 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage };
  }
};

// 이메일/비밀번호 회원가입
export const signUpWithEmail = async (email: string, password: string, displayName: string) => {
  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    
    // 사용자 프로필 업데이트
    if (result.user) {
      await saveUserToFirestore(result.user);
    }
    
    return { success: true, user: result.user };
  } catch (error) {
    console.error('회원가입 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage };
  }
};

// 이메일/비밀번호 로그인
export const signInWithEmail = async (email: string, password: string) => {
  try {
    const result = await signInWithEmailAndPassword(auth, email, password);
    return { success: true, user: result.user };
  } catch (error) {
    console.error('로그인 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage };
  }
};

// 로그아웃
export const signOutUser = async () => {
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    console.error('로그아웃 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage };
  }
};

// 사용자 정보를 Firestore에 저장
const saveUserToFirestore = async (user: User | any) => {
  try {
    const userRef = doc(db, 'users', user.uid);
    await setDoc(userRef, {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoURL: user.photoURL,
      createdAt: new Date(),
      lastLoginAt: new Date()
    }, { merge: true });
  } catch (error) {
    console.error('사용자 정보 저장 실패:', error);
  }
};

// 현재 사용자 가져오기
export const getCurrentUser = (): User | null => {
  return auth.currentUser;
};

// 인증 상태 변경 감지
export const onAuthStateChange = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(auth, callback);
};

// 건강 데이터 저장
export const saveHealthData = async (userId: string, data: any) => {
  try {
    const healthRef = collection(db, 'healthData');
    await addDoc(healthRef, {
      userId,
      ...data,
      timestamp: new Date()
    });
    return { success: true };
  } catch (error) {
    console.error('건강 데이터 저장 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage };
  }
};

// 사용자의 건강 데이터 가져오기
export const getUserHealthData = async (userId: string, limitCount: number = 10) => {
  try {
    const healthRef = collection(db, 'healthData');
    const q = query(
      healthRef,
      where('userId', '==', userId),
      orderBy('timestamp', 'desc'),
      limit(limitCount)
    );
    
    const snapshot = await getDocs(q);
    const data = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    return { success: true, data };
  } catch (error) {
    console.error('건강 데이터 가져오기 실패:', error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    return { success: false, error: errorMessage, data: [] };
  }
};

// 음악 사용량 제한 확인
export const checkMusicUsageLimit = async (userId: string): Promise<{ canUse: boolean; remainingUses: number }> => {
  try {
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    
    if (userDoc.exists()) {
      const userData = userDoc.data();
      const musicUsage = userData.musicUsage || 0;
      const maxUsage = userData.subscription === 'premium' ? 100 : 10; // 프리미엄: 100회, 무료: 10회
      
      return {
        canUse: musicUsage < maxUsage,
        remainingUses: Math.max(0, maxUsage - musicUsage)
      };
    }
    
    return { canUse: true, remainingUses: 10 }; // 기본값
  } catch (error) {
    console.error('음악 사용량 확인 실패:', error);
    return { canUse: false, remainingUses: 0 };
  }
};

// 음악 사용량 증가
export const incrementMusicUsage = async (userId: string): Promise<{ success: boolean }> => {
  try {
    const userRef = doc(db, 'users', userId);
    await setDoc(userRef, {
      musicUsage: (await getDoc(userRef)).data()?.musicUsage || 0 + 1
    }, { merge: true });
    
    return { success: true };
  } catch (error) {
    console.error('음악 사용량 증가 실패:', error);
    return { success: false };
  }
};

export default app; 