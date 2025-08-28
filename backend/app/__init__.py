
import logging

logger = logging.getLogger(__name__)

def init_cache(app):
    @app.on_event("startup")
    async def startup():
        logger.info("✅ 캐시 시스템 없이 서버 시작")
        # 캐시 시스템 비활성화 - 성능 최적화는 MediaPipe 지연 초기화로만 진행