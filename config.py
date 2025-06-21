import os
from datetime import timedelta

class Config:
    # 기본 Flask 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-for-development'
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 최대 파일 크기
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Gemini API 설정
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'YOUR_API_KEY_HERE'
    
    # 개발/프로덕션 환경 구분
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
    def __init__(self):
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        if not self.SECRET_KEY:
            raise ValueError("프로덕션 환경에서는 SECRET_KEY 환경변수가 필요합니다.")

# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
