#!/usr/bin/env python3
"""
스마트 냉장고 레시피 추천 애플리케이션 실행 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드 (있는 경우)
load_dotenv()

# 애플리케이션 import
try:
    from enhanced_app import create_app
except ImportError:
    print("enhanced_app.py 파일을 찾을 수 없습니다.")
    print("현재 디렉토리에 enhanced_app.py 파일이 있는지 확인해주세요.")
    sys.exit(1)

def main():
    """메인 실행 함수"""
    
    # API 키 확인
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key or api_key == 'your-gemini-api-key-here':
        print("⚠️  경고: Gemini API 키가 설정되지 않았습니다.")
        print("1. Google AI Studio (https://makersuite.google.com/app/apikey)에서 API 키를 발급받으세요.")
        print("2. .env 파일을 생성하고 GEMINI_API_KEY=your_api_key 를 추가하거나")
        print("3. enhanced_app.py의 GEMINI_API_KEY 변수를 직접 수정하세요.")
        print()
        
        response = input("API 키 없이 계속 진행하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Flask 앱 생성
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    
    # 필요한 디렉토리 생성
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    print("🚀 스마트 냉장고 레시피 추천 애플리케이션을 시작합니다...")
    print(f"📁 설정: {config_name}")
    print(f"🌐 URL: http://localhost:5000")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print()
    
    try:
        # 서버 실행
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=app.config.get('DEBUG', False)
        )
    except KeyboardInterrupt:
        print("\n👋 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
