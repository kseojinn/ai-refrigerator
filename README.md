# AI 냉장고 레시피 추천 시스템

VLM(Vision Language Model)과 LLM(Large Language Model)을 활용한 지능형 냉장고 관리 및 레시피 추천 웹 애플리케이션입니다.

## 프로젝트 개요

식재료 사진을 업로드하면 AI가 자동으로 인식하여 냉장고를 관리하고, 보유한 재료를 기반으로 맞춤형 레시피를 추천해주는 시스템입니다.

### 주요 기능

- **VLM 활용**: 식재료 이미지 인식 및 자동 분류 (냉동/냉장/야채/실온)
- **LLM 활용**: 보유 재료 기반 5가지 카테고리 레시피 추천 (한식/중식/일식/양식/기타)
- **커스텀 검색**: 원하는 요리명 입력 시 레시피 및 부족한 재료 분석
- **재료 관리**: 요리 완료 시 사용된 재료 자동 소비 처리

## 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Model**: Google Gemini 2.5 Flash
- **Image Processing**: PIL (Pillow)

## 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/kseojinn/ai-refrigerator.git
cd ai-refrigerator
```

### 2. 가상환경 설정
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
1. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 Gemini API 키 발급
2. API 키 설정:

```bash
# .env 파일 생성
GEMINI_API_KEY=api_key_here
```

### 5. 애플리케이션 실행
```bash
python run.py
```

브라우저에서 `http://localhost:5000` 접속

## 사용법

### 1. 식재료 추가
- 식재료가 포함된 사진을 드래그 앤 드롭 또는 파일 선택으로 업로드
- AI가 자동으로 식재료를 인식하고 적절한 카테고리에 분류

### 2. 레시피 확인
- 한식, 중식, 일식, 양식, 기타 탭에서 추천 레시피 확인
- 각 레시피는 보유한 재료만으로 만들 수 있는 현실적인 요리

### 3. 요리 완료
- 레시피의 "요리 완료" 버튼 클릭 시 사용된 재료가 냉장고에서 자동 제거

### 4. 커스텀 레시피 검색
- 만들고 싶은 요리명 입력
- 필요한 재료, 보유한 재료, 부족한 재료 분석 결과 제공

## 프로젝트 구조

```
ai-refrigerator/
├── enhanced_app.py      # Flask 메인 애플리케이션
├── config.py           # 설정 파일
├── run.py             # 실행 스크립트
├── requirements.txt    # 패키지 의존성
├── templates/
│   └── index.html     # HTML 템플릿
├── static/
│   └── uploads/       # 업로드 파일 임시 저장
└── README.md
```

## AI 모델 활용

### VLM (Vision Language Model)
```python
def analyze_ingredients_image(image_path):
    # Gemini 2.5 Flash를 사용하여 이미지에서 식재료 인식
    # 냉동/냉장/야채/실온 카테고리로 자동 분류
```

### LLM (Large Language Model)
```python
def generate_recipes(ingredients_dict):
    # 보유 재료를 기반으로 5가지 카테고리 레시피 생성
    # 한식, 중식, 일식, 양식, 기타

def generate_custom_recipe(dish_name, available_ingredients):
    # 사용자 요청 요리에 대한 재료 분석 및 레시피 제공
```

## 스크린샷

### 메인 화면
- 현대적인 그라디언트 디자인
- 직관적인 드래그 앤 드롭 업로드
- 냉장고 상태 실시간 표시

### 레시피 추천
- 5가지 카테고리별 탭 구성
- 재료와 조리법 상세 표시
- 요리 완료 기능

## 개발 환경

- Python 3.9+
- Flask 2.3.3
- Google Gemini API
- Modern Web Browsers

## 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.
