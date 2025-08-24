# app.api.v1 패키지 초기화

try:
	from .api import api_router  # noqa: F401
except Exception:
	# api_router가 없을 수 있음
	api_router = None  # type: ignore
