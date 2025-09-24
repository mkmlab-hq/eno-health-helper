import firebase_admin
from firebase_admin import credentials, firestore, storage
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from ..models.user_measurement import (
    UserMeasurement, MeasurementPair, ComparisonResult,
    UserMeasurementSummary
)

logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase 연동 서비스 - 사용자 측정 데이터 관리"""
    
    def __init__(self):
        """Firebase 서비스 초기화"""
        try:
            # Firebase 앱이 이미 초기화되어 있는지 확인
            if not firebase_admin._apps:
                # Firebase 인증 정보 설정
                cred = credentials.Certificate("path/to/serviceAccountKey.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'eno-health-helper.appspot.com'
                })
            
            # Firestore 및 Storage 클라이언트 초기화
            self.db = firestore.client()
            self.bucket = storage.bucket()
            logger.info("Firebase 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"Firebase 서비스 초기화 실패: {e}")
            self.db = None
            self.bucket = None
    
    async def get_user_measurements(
        self, 
        user_id: str, 
        days_back: int = 30
    ) -> List[UserMeasurement]:
        """
        사용자의 측정 기록을 조회
        
        Args:
            user_id: 사용자 ID
            days_back: 몇 일 전까지의 데이터를 가져올지
        
        Returns:
            List[UserMeasurement]: 측정 기록 목록
        """
        try:
            if not self.db:
                logger.error("Firestore 데이터베이스가 초기화되지 않음")
                return []
            
            # 날짜 범위 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Firestore에서 사용자 측정 데이터 조회
            measurements_ref = self.db.collection('user_measurements')
            query = measurements_ref.where('user_id', '==', user_id)\
                                 .where('timestamp', '>=', start_date)\
                                 .order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            docs = query.stream()
            measurements = []
            
            for doc in docs:
                try:
                    data = doc.to_dict()
                    # Firestore Timestamp를 Python datetime으로 변환
                    if 'timestamp' in data:
                        data['timestamp'] = data['timestamp'].timestamp()
                        data['timestamp'] = datetime.fromtimestamp(data['timestamp'])
                    if 'created_at' in data:
                        data['created_at'] = data['created_at'].timestamp()
                        data['created_at'] = datetime.fromtimestamp(data['created_at'])
                    
                    measurement = UserMeasurement(**data)
                    measurements.append(measurement)
                    
                except Exception as e:
                    logger.warning(f"측정 데이터 파싱 실패 (doc_id: {doc.id}): {e}")
                    continue
            
            logger.info(f"사용자 {user_id}의 측정 기록 {len(measurements)}개 조회 완료")
            return measurements
            
        except Exception as e:
            logger.error(f"사용자 측정 기록 조회 실패: {e}")
            return []
    
    async def get_measurement_pair(
        self, 
        user_id: str, 
        pair_id: str
    ) -> Optional[MeasurementPair]:
        """
        특정 측정 페어 조회
        
        Args:
            user_id: 사용자 ID
            pair_id: 페어 ID
        
        Returns:
            Optional[MeasurementPair]: 측정 페어 데이터
        """
        try:
            if not self.db:
                logger.error("Firestore 데이터베이스가 초기화되지 않음")
                return None
            
            # Firestore에서 측정 페어 데이터 조회
            pair_ref = self.db.collection('measurement_pairs').document(pair_id)
            pair_doc = pair_ref.get()
            
            if not pair_doc.exists:
                logger.warning(f"측정 페어 {pair_id}를 찾을 수 없음")
                return None
            
            data = pair_doc.to_dict()
            
            # 사용자 ID 검증
            if data.get('user_id') != user_id:
                logger.warning(f"사용자 {user_id}의 측정 페어 {pair_id}가 아님")
                return None
            
            # Firestore Timestamp를 Python datetime으로 변환
            if 'created_at' in data:
                data['created_at'] = data['created_at'].timestamp()
                data['created_at'] = datetime.fromtimestamp(data['created_at'])
            
            # before_measurement와 after_measurement도 변환
            if 'before_measurement' in data:
                before_data = data['before_measurement']
                if 'timestamp' in before_data:
                    before_data['timestamp'] = before_data['timestamp'].timestamp()
                    before_data['timestamp'] = datetime.fromtimestamp(before_data['timestamp'])
                if 'created_at' in before_data:
                    before_data['created_at'] = before_data['created_at'].timestamp()
                    before_data['created_at'] = datetime.fromtimestamp(before_data['created_at'])
            
            if 'after_measurement' in data:
                after_data = data['after_measurement']
                if 'timestamp' in after_data:
                    after_data['timestamp'] = after_data['timestamp'].timestamp()
                    after_data['timestamp'] = datetime.fromtimestamp(after_data['timestamp'])
                if 'created_at' in after_data:
                    after_data['created_at'] = after_data['created_at'].timestamp()
                    after_data['created_at'] = datetime.fromtimestamp(after_data['created_at'])
            
            pair = MeasurementPair(**data)
            logger.info(f"측정 페어 {pair_id} 조회 완료")
            return pair
            
        except Exception as e:
            logger.error(f"측정 페어 조회 실패: {e}")
            return None
    
    async def save_measurement_pair(
        self, 
        pair: MeasurementPair
    ) -> bool:
        """
        측정 페어를 Firestore에 저장
        
        Args:
            pair: 저장할 측정 페어 데이터
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            if not self.db:
                logger.error("Firestore 데이터베이스가 초기화되지 않음")
                return False
            
            # Pydantic 모델을 딕셔너리로 변환
            pair_data = pair.dict()
            
            # Python datetime을 Firestore Timestamp로 변환
            if 'created_at' in pair_data:
                pair_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            if 'before_measurement' in pair_data:
                before_data = pair_data['before_measurement']
                if 'created_at' in before_data:
                    before_data['created_at'] = firestore.SERVER_TIMESTAMP
                if 'timestamp' in before_data:
                    before_data['timestamp'] = firestore.Timestamp.from_date(
                        before_data['timestamp']
                    )
            
            if 'after_measurement' in pair_data:
                after_data = pair_data['after_measurement']
                if 'created_at' in after_data:
                    after_data['created_at'] = firestore.SERVER_TIMESTAMP
                if 'timestamp' in after_data:
                    after_data['timestamp'] = firestore.Timestamp.from_date(
                        after_data['timestamp']
                    )
            
            # Firestore에 저장
            pair_ref = self.db.collection('measurement_pairs').document(pair.pair_id)
            pair_ref.set(pair_data)
            
            logger.info(f"측정 페어 {pair.pair_id} 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"측정 페어 저장 실패: {e}")
            return False
    
    async def get_user_measurement_summary(
        self, 
        user_id: str
    ) -> Optional[UserMeasurementSummary]:
        """
        사용자의 측정 요약 정보 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            Optional[UserMeasurementSummary]: 측정 요약 정보
        """
        try:
            # 사용자의 모든 측정 기록 조회
            measurements = await self.get_user_measurements(user_id, days_back=365)
            
            if not measurements:
                return UserMeasurementSummary(
                    user_id=user_id,
                    total_measurements=0,
                    total_pairs=0,
                    average_improvement_rate=0.0,
                    last_measurement_date=None
                )
            
            # 측정 페어 생성
            pairs = self._create_measurement_pairs(measurements)
            
            # 요약 정보 계산
            total_measurements = len(measurements)
            total_pairs = len(pairs)
            last_measurement_date = max(m.timestamp for m in measurements)
            
            # 평균 개선률 계산
            if pairs:
                improvement_rates = []
                for pair in pairs:
                    before_score = pair.before_measurement.overall_health_score
                    after_score = pair.after_measurement.overall_health_score
                    if before_score > 0:
                        improvement_rate = ((after_score - before_score) / before_score) * 100
                        improvement_rates.append(improvement_rate)
                
                average_improvement_rate = sum(improvement_rates) / len(improvement_rates) if improvement_rates else 0.0
            else:
                average_improvement_rate = 0.0
            
            summary = UserMeasurementSummary(
                user_id=user_id,
                total_measurements=total_measurements,
                total_pairs=total_pairs,
                average_improvement_rate=average_improvement_rate,
                last_measurement_date=last_measurement_date
            )
            
            logger.info(f"사용자 {user_id}의 측정 요약 정보 조회 완료")
            return summary
            
        except Exception as e:
            logger.error(f"사용자 측정 요약 정보 조회 실패: {e}")
            return None
    
    def _create_measurement_pairs(
        self, 
        measurements: List[UserMeasurement]
    ) -> List[MeasurementPair]:
        """
        30분 전후 측정 페어를 자동으로 생성 (내부 메서드)
        
        Args:
            measurements: 사용자의 모든 측정 기록
        
        Returns:
            List[MeasurementPair]: 30분 전후 측정 페어 목록
        """
        pairs = []
        sorted_measurements = sorted(measurements, key=lambda x: x.timestamp)
        
        for i, measurement in enumerate(sorted_measurements):
            # 30분 ± 10분 범위 내의 다음 측정 찾기
            for j in range(i + 1, len(sorted_measurements)):
                next_measurement = sorted_measurements[j]
                time_diff = next_measurement.timestamp - measurement.timestamp
                
                # 20분 ~ 40분 범위 내인 경우 페어 생성
                if timedelta(minutes=20) <= time_diff <= timedelta(minutes=40):
                    pair = MeasurementPair(
                        pair_id=f"pair_{len(pairs) + 1}",
                        before_measurement=measurement,
                        after_measurement=next_measurement,
                        time_interval_minutes=time_diff.total_seconds() / 60,
                        created_at=datetime.now()
                    )
                    pairs.append(pair)
                    break  # 첫 번째 매칭된 페어만 생성
        
        return pairs
