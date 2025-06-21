from flask import Flask, render_template, request, jsonify, session
import os
import base64
from google import genai
import json
from werkzeug.utils import secure_filename
import uuid
from config import config
import logging
from datetime import datetime

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 로깅 설정
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # 업로드 폴더 생성
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Gemini API 클라이언트 설정
    try:
        client = genai.Client(api_key=app.config['GEMINI_API_KEY'])
        app.logger.info("Gemini API 클라이언트 초기화 완료")
    except Exception as e:
        app.logger.error(f"Gemini API 클라이언트 초기화 실패: {e}")
        client = None

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def validate_and_parse_json(response_text):
        """JSON 응답 검증 및 파싱"""
        try:
            # 마크다운 코드 블록 제거
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            app.logger.error(f"JSON 파싱 오류: {e}")
            return None

    def analyze_ingredients_image(image_path):
        """VLM을 사용하여 이미지에서 식재료 인식 및 분류"""
        if not client:
            return {"냉동": [], "냉장": [], "야채": [], "실온": []}
        
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            prompt = """
            이 이미지에서 보이는 모든 식재료를 정확히 인식하고 다음 카테고리로 분류해주세요:
            
            분류 기준:
            - 냉동: 냉동보관이 필요한 식재료 (육류, 생선, 냉동식품, 아이스크림 등)
            - 냉장: 냉장보관이 필요한 식재료 (유제품, 계란, 두부, 김치 등)
            - 야채: 채소류 (상추, 양파, 당근, 토마토, 브로콜리 등)
            - 실온: 실온보관 가능한 식재료 (쌀, 라면, 통조림, 조미료, 과일 등)
            
            다음 JSON 형식으로만 응답해주세요. 다른 텍스트는 포함하지 마세요:
            {
                "냉동": ["재료1", "재료2"],
                "냉장": ["재료3", "재료4"],
                "야채": ["재료5", "재료6"],
                "실온": ["재료7", "재료8"]
            }
            
            주의사항:
            - 한국어로 식재료명을 정확히 작성
            - 포장지나 용기가 아닌 실제 식재료만 인식
            - 확실하지 않은 것은 포함하지 않음
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_data).decode()}}
                        ]
                    }
                ]
            )
            
            result = validate_and_parse_json(response.text)
            if result:
                app.logger.info(f"이미지 분석 완료: {result}")
                return result
            else:
                return {"냉동": [], "냉장": [], "야채": [], "실온": []}
                
        except Exception as e:
            app.logger.error(f"이미지 분석 오류: {e}")
            return {"냉동": [], "냉장": [], "야채": [], "실온": []}

    def generate_recipes(ingredients_dict):
        """LLM을 사용하여 레시피 생성"""
        if not client:
            return {}
        
        try:
            all_ingredients = []
            for category, items in ingredients_dict.items():
                all_ingredients.extend(items)
            
            if not all_ingredients:
                return {}
            
            ingredients_text = ", ".join(all_ingredients)
            
            prompt = f"""
            다음 식재료들을 사용하여 5가지 카테고리의 요리 레시피를 각각 1개씩 추천해주세요.
            
            사용 가능한 식재료: {ingredients_text}
            
            요구사항:
            1. 주어진 식재료만으로 만들 수 있는 현실적인 요리
            2. 각 카테고리별로 대표적인 요리 1개씩
            3. 조리법은 간단하고 명확하게
            
            다음 JSON 형식으로만 응답해주세요:
            {{
                "한식": {{
                    "음식명": "요리명",
                    "재료": ["재료1", "재료2", "재료3"],
                    "조리법": [" 첫 번째 단계", " 두 번째 단계", " 세 번째 단계"]
                }},
                "중식": {{
                    "음식명": "요리명",
                    "재료": ["재료1", "재료2"],
                    "조리법": [" 첫 번째 단계", " 두 번째 단계"]
                }},
                "일식": {{
                    "음식명": "요리명",
                    "재료": ["재료1", "재료2"],
                    "조리법": [" 첫 번째 단계", " 두 번째 단계"]
                }},
                "양식": {{
                    "음식명": "요리명",
                    "재료": ["재료1", "재료2"],
                    "조리법": [" 첫 번째 단계", " 두 번째 단계"]
                }},
                "기타": {{
                    "음식명": "요리명",
                    "재료": ["재료1", "재료2"],
                    "조리법": [" 첫 번째 단계", " 두 번째 단계"]
                }}
            }}
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            result = validate_and_parse_json(response.text)
            if result:
                app.logger.info("레시피 생성 완료")
                return result
            else:
                return {}
                
        except Exception as e:
            app.logger.error(f"레시피 생성 오류: {e}")
            return {}

    def generate_custom_recipe(dish_name, available_ingredients):
        """사용자가 입력한 요리에 대한 레시피 생성"""
        if not client:
            return {}
        
        try:
            ingredients_text = ", ".join(available_ingredients) if available_ingredients else "없음"
            
            prompt = f"""
            "{dish_name}" 요리를 만들고 싶습니다.
            현재 보유한 식재료: {ingredients_text}
            
            다음 사항을 분석해서 JSON으로 응답해주세요:
            1. 이 요리를 만들기 위해 필요한 모든 재료
            2. 현재 보유한 재료 중 사용 가능한 것들
            3. 부족한 재료들
            4. 상세한 조리법
            5. 부족한 재료 구매 추천
            
            JSON 형식:
            {{
                "음식명": "{dish_name}",
                "필요한_재료": ["재료1", "재료2", "재료3"],
                "보유한_재료": ["보유재료1", "보유재료2"],
                "부족한_재료": ["부족재료1", "부족재료2"],
                "조리법": [" 첫 번째 단계", " 두 번째 단계", " 세 번째 단계"],
                "재료_구매_추천": ["마트에서 구매할 재료1", "마트에서 구매할 재료2"]
            }}
            
            현실적이고 정확한 레시피를 제공해주세요.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            result = validate_and_parse_json(response.text)
            if result:
                app.logger.info(f"커스텀 레시피 생성 완료: {dish_name}")
                return result
            else:
                return {}
                
        except Exception as e:
            app.logger.error(f"커스텀 레시피 생성 오류: {e}")
            return {}

    # 라우트 정의
    @app.route('/')
    def index():
        if 'refrigerator' not in session:
            session['refrigerator'] = {"냉동": [], "냉장": [], "야채": [], "실온": []}
        return render_template('index.html')

    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '지원하지 않는 파일 형식입니다. (JPG, PNG, GIF만 가능)'}), 400
        
        try:
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # VLM으로 이미지 분석
            ingredients = analyze_ingredients_image(filepath)
            
            # 세션의 냉장고에 추가
            if 'refrigerator' not in session:
                session['refrigerator'] = {"냉동": [], "냉장": [], "야채": [], "실온": []}
            
            # 중복 제거하며 추가
            for category, items in ingredients.items():
                for item in items:
                    if item not in session['refrigerator'][category]:
                        session['refrigerator'][category].append(item)
            
            session.modified = True
            
            # 임시 파일 삭제
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'ingredients': ingredients,
                'refrigerator': session['refrigerator']
            })
            
        except Exception as e:
            app.logger.error(f"이미지 업로드 처리 오류: {e}")
            return jsonify({'error': '이미지 처리 중 오류가 발생했습니다.'}), 500

    @app.route('/get_recipes', methods=['GET'])
    def get_recipes():
        if 'refrigerator' not in session:
            return jsonify({'error': '냉장고가 비어있습니다.'}), 400
        
        # 재료가 있는지 확인
        total_ingredients = sum(len(items) for items in session['refrigerator'].values())
        if total_ingredients == 0:
            return jsonify({'recipes': {}})
        
        recipes = generate_recipes(session['refrigerator'])
        return jsonify({'recipes': recipes})

    @app.route('/cook_recipe', methods=['POST'])
    def cook_recipe():
        try:
            data = request.get_json()
            used_ingredients = data.get('ingredients', [])
            
            if 'refrigerator' not in session:
                return jsonify({'error': '냉장고가 비어있습니다.'}), 400
            
            # 사용된 재료를 냉장고에서 제거
            removed_count = 0
            for ingredient in used_ingredients:
                for category in session['refrigerator']:
                    if ingredient in session['refrigerator'][category]:
                        session['refrigerator'][category].remove(ingredient)
                        removed_count += 1
                        break
            
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': f'요리가 완료되었습니다! {removed_count}개의 재료가 사용되었습니다.',
                'refrigerator': session['refrigerator']
            })
            
        except Exception as e:
            app.logger.error(f"요리 완료 처리 오류: {e}")
            return jsonify({'error': '요리 완료 처리 중 오류가 발생했습니다.'}), 500

    @app.route('/custom_recipe', methods=['POST'])
    def custom_recipe():
        try:
            data = request.get_json()
            dish_name = data.get('dish_name', '').strip()
            
            if not dish_name:
                return jsonify({'error': '요리명을 입력해주세요.'}), 400
            
            if 'refrigerator' not in session:
                session['refrigerator'] = {"냉동": [], "냉장": [], "야채": [], "실온": []}
            
            # 모든 보유 재료 수집
            all_ingredients = []
            for category, items in session['refrigerator'].items():
                all_ingredients.extend(items)
            
            recipe = generate_custom_recipe(dish_name, all_ingredients)
            
            if recipe:
                return jsonify({'recipe': recipe})
            else:
                return jsonify({'error': '레시피를 생성할 수 없습니다.'}), 500
                
        except Exception as e:
            app.logger.error(f"커스텀 레시피 처리 오류: {e}")
            return jsonify({'error': '레시피 검색 중 오류가 발생했습니다.'}), 500

    @app.route('/get_refrigerator', methods=['GET'])
    def get_refrigerator():
        if 'refrigerator' not in session:
            session['refrigerator'] = {"냉동": [], "냉장": [], "야채": [], "실온": []}
        
        return jsonify({'refrigerator': session['refrigerator']})

    @app.route('/clear_refrigerator', methods=['POST'])
    def clear_refrigerator():
        session['refrigerator'] = {"냉동": [], "냉장": [], "야채": [], "실온": []}
        session.modified = True
        return jsonify({'success': True, 'message': '냉장고가 비워졌습니다.'})

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': '파일 크기가 너무 큽니다. (최대 16MB)'}), 413

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"내부 서버 오류: {e}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

    return app

if __name__ == '__main__':
    # 환경 설정
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    
    # 개발 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
