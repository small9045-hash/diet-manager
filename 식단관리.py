import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="식단 관리 프로그램",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f8faf8 0%, #e8f5e9 100%); }
    .title-box {
        background: linear-gradient(135deg, #2e7d32, #66bb6a);
        padding: 2rem; border-radius: 16px; text-align: center;
        color: white; margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(46,125,50,0.3);
    }
    .title-box h1 { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .title-box p { font-size: 1rem; margin: 0.5rem 0 0 0; opacity: 0.9; }
    .card {
        background: white; border-radius: 16px; padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.3rem; font-weight: 700; color: #2e7d32;
        margin-bottom: 1rem; padding-bottom: 0.5rem;
        border-bottom: 2px solid #e8f5e9;
    }
    .stButton > button {
        background: linear-gradient(135deg, #2e7d32, #66bb6a);
        color: white; border: none; border-radius: 10px;
        padding: 0.6rem 2rem; font-family: 'Noto Sans KR', sans-serif;
        font-weight: 500; font-size: 1rem; width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1b5e20, #43a047);
        box-shadow: 0 4px 15px rgba(46,125,50,0.4);
    }
    .back-btn > button {
        background: #f5f5f5 !important;
        color: #333 !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 한국 음식 영양소 DB (100g 기준)
# ============================================================
FOOD_DB = {
    # 밥류
    "흰쌀밥": {"칼로리": 130, "탄수화물": 28, "단백질": 2.5, "지방": 0.3},
    "현미밥": {"칼로리": 145, "탄수화물": 30, "단백질": 3, "지방": 0.9},
    "잡곡밥": {"칼로리": 140, "탄수화물": 29, "단백질": 3, "지방": 0.8},
    "볶음밥": {"칼로리": 180, "탄수화물": 30, "단백질": 4, "지방": 5},
    "김밥": {"칼로리": 170, "탄수화물": 28, "단백질": 5, "지방": 4},
    "쌀밥": {"칼로리": 130, "탄수화물": 28, "단백질": 2.5, "지방": 0.3},
    # 면류
    "라면": {"칼로리": 450, "탄수화물": 65, "단백질": 10, "지방": 16},
    "냉면": {"칼로리": 280, "탄수화물": 55, "단백질": 8, "지방": 3},
    "짜장면": {"칼로리": 480, "탄수화물": 75, "단백질": 12, "지방": 14},
    "짬뽕": {"칼로리": 420, "탄수화물": 55, "단백질": 18, "지방": 12},
    "국수": {"칼로리": 350, "탄수화물": 68, "단백질": 10, "지방": 2},
    "우동": {"칼로리": 320, "탄수화물": 60, "단백질": 9, "지방": 3},
    "파스타": {"칼로리": 380, "탄수화물": 65, "단백질": 13, "지방": 7},
    "스파게티": {"칼로리": 380, "탄수화물": 65, "단백질": 13, "지방": 7},
    # 고기류
    "닭가슴살": {"칼로리": 165, "탄수화물": 0, "단백질": 31, "지방": 3.6},
    "삼겹살": {"칼로리": 331, "탄수화물": 0, "단백질": 18, "지방": 28},
    "소고기": {"칼로리": 250, "탄수화물": 0, "단백질": 26, "지방": 15},
    "돼지고기": {"칼로리": 242, "탄수화물": 0, "단백질": 27, "지방": 14},
    "닭다리": {"칼로리": 215, "탄수화물": 0, "단백질": 26, "지방": 12},
    "불고기": {"칼로리": 200, "탄수화물": 8, "단백질": 22, "지방": 10},
    "제육볶음": {"칼로리": 250, "탄수화물": 10, "단백질": 20, "지방": 15},
    "갈비": {"칼로리": 300, "탄수화물": 5, "단백질": 25, "지방": 20},
    "치킨": {"칼로리": 280, "탄수화물": 10, "단백질": 27, "지방": 15},
    "햄버거": {"칼로리": 295, "탄수화물": 30, "단백질": 15, "지방": 14},
    # 생선/해산물
    "연어": {"칼로리": 208, "탄수화물": 0, "단백질": 20, "지방": 13},
    "고등어": {"칼로리": 205, "탄수화물": 0, "단백질": 19, "지방": 13},
    "참치": {"칼로리": 132, "탄수화물": 0, "단백질": 28, "지방": 1.3},
    "새우": {"칼로리": 99, "탄수화물": 0, "단백질": 24, "지방": 0.3},
    "오징어": {"칼로리": 92, "탄수화물": 3, "단백질": 18, "지방": 1.2},
    "갈치": {"칼로리": 130, "탄수화물": 0, "단백질": 21, "지방": 5},
    # 채소류
    "김치": {"칼로리": 18, "탄수화물": 4, "단백질": 1, "지방": 0.1},
    "시금치": {"칼로리": 23, "탄수화물": 3.6, "단백질": 2.9, "지방": 0.4},
    "브로콜리": {"칼로리": 34, "탄수화물": 7, "단백질": 2.8, "지방": 0.4},
    "상추": {"칼로리": 15, "탄수화물": 2.9, "단백질": 1.4, "지방": 0.2},
    "양배추": {"칼로리": 25, "탄수화물": 5.8, "단백질": 1.3, "지방": 0.1},
    "당근": {"칼로리": 41, "탄수화물": 9.6, "단백질": 0.9, "지방": 0.2},
    "오이": {"칼로리": 15, "탄수화물": 3.6, "단백질": 0.7, "지방": 0.1},
    "토마토": {"칼로리": 18, "탄수화물": 3.9, "단백질": 0.9, "지방": 0.2},
    "샐러드": {"칼로리": 20, "탄수화물": 3, "단백질": 1.5, "지방": 0.3},
    # 탄수화물류
    "고구마": {"칼로리": 86, "탄수화물": 20, "단백질": 1.6, "지방": 0.1},
    "감자": {"칼로리": 77, "탄수화물": 17, "단백질": 2, "지방": 0.1},
    "옥수수": {"칼로리": 96, "탄수화물": 21, "단백질": 3.4, "지방": 1.5},
    "식빵": {"칼로리": 265, "탄수화물": 49, "단백질": 9, "지방": 3.5},
    "오트밀": {"칼로리": 389, "탄수화물": 66, "단백질": 17, "지방": 7},
    "빵": {"칼로리": 265, "탄수화물": 49, "단백질": 9, "지방": 3.5},
    # 유제품/계란
    "계란": {"칼로리": 155, "탄수화물": 1.1, "단백질": 13, "지방": 11},
    "삶은계란": {"칼로리": 155, "탄수화물": 1.1, "단백질": 13, "지방": 11},
    "삶은 계란": {"칼로리": 155, "탄수화물": 1.1, "단백질": 13, "지방": 11},
    "우유": {"칼로리": 61, "탄수화물": 4.8, "단백질": 3.2, "지방": 3.3},
    "두부": {"칼로리": 76, "탄수화물": 1.9, "단백질": 8, "지방": 4.2},
    "그릭요거트": {"칼로리": 59, "탄수화물": 3.6, "단백질": 10, "지방": 0.4},
    "요거트": {"칼로리": 61, "탄수화물": 7, "단백질": 3.5, "지방": 1.6},
    "치즈": {"칼로리": 402, "탄수화물": 1.3, "단백질": 25, "지방": 33},
    # 과일류
    "바나나": {"칼로리": 89, "탄수화물": 23, "단백질": 1.1, "지방": 0.3},
    "사과": {"칼로리": 52, "탄수화물": 14, "단백질": 0.3, "지방": 0.2},
    "귤": {"칼로리": 53, "탄수화물": 13, "단백질": 0.8, "지방": 0.3},
    "포도": {"칼로리": 69, "탄수화물": 18, "단백질": 0.7, "지방": 0.2},
    "수박": {"칼로리": 30, "탄수화물": 7.6, "단백질": 0.6, "지방": 0.2},
    "딸기": {"칼로리": 32, "탄수화물": 7.7, "단백질": 0.7, "지방": 0.3},
    # 국/찌개류
    "된장찌개": {"칼로리": 80, "탄수화물": 8, "단백질": 6, "지방": 3},
    "김치찌개": {"칼로리": 90, "탄수화물": 7, "단백질": 7, "지방": 4},
    "순두부찌개": {"칼로리": 120, "탄수화물": 6, "단백질": 10, "지방": 6},
    "미역국": {"칼로리": 40, "탄수화물": 4, "단백질": 3, "지방": 1.5},
    "설렁탕": {"칼로리": 120, "탄수화물": 5, "단백질": 15, "지방": 5},
    "삼계탕": {"칼로리": 180, "탄수화물": 10, "단백질": 20, "지방": 7},
    "된장국": {"칼로리": 50, "탄수화물": 5, "단백질": 4, "지방": 2},
    # 기타
    "피자": {"칼로리": 266, "탄수화물": 33, "단백질": 11, "지방": 10},
    "떡볶이": {"칼로리": 180, "탄수화물": 38, "단백질": 4, "지방": 2},
    "순대": {"칼로리": 190, "탄수화물": 20, "단백질": 10, "지방": 8},
    "튀김": {"칼로리": 300, "탄수화물": 25, "단백질": 8, "지방": 18},
    "아몬드": {"칼로리": 579, "탄수화물": 22, "단백질": 21, "지방": 50},
    "견과류": {"칼로리": 550, "탄수화물": 20, "단백질": 18, "지방": 45},
    "단백질 쉐이크": {"칼로리": 120, "탄수화물": 5, "단백질": 25, "지방": 2},
    "프로틴": {"칼로리": 120, "탄수화물": 5, "단백질": 25, "지방": 2},
    "나물": {"칼로리": 60, "탄수화물": 8, "단백질": 3, "지방": 2},
    "콩나물": {"칼로리": 30, "탄수화물": 3, "단백질": 3, "지방": 1},
}

# ============================================================
# 음식 검색 함수 (DB 기반)
# ============================================================
def search_food(food_name):
    food_name = food_name.strip()
    # 정확히 일치
    if food_name in FOOD_DB:
        data = FOOD_DB[food_name]
        return {"음식명": food_name, **data}
    # 부분 일치
    for key in FOOD_DB:
        if food_name in key or key in food_name:
            data = FOOD_DB[key]
            return {"음식명": key, **data}
    return None

# ============================================================
# 나이대별 1일 영양소 권장량
# ============================================================
NUTRIENT_STANDARDS = {
    "10대 남성 (13-18세)": {"칼로리": 2700, "탄수화물": 405, "단백질": 65, "지방": 75},
    "10대 여성 (13-18세)": {"칼로리": 2000, "탄수화물": 300, "단백질": 55, "지방": 55},
    "20대 남성 (19-29세)": {"칼로리": 2600, "탄수화물": 390, "단백질": 65, "지방": 72},
    "20대 여성 (19-29세)": {"칼로리": 2000, "탄수화물": 300, "단백질": 55, "지방": 55},
    "30대 남성 (30-49세)": {"칼로리": 2500, "탄수화물": 375, "단백질": 65, "지방": 69},
    "30대 여성 (30-49세)": {"칼로리": 1900, "탄수화물": 285, "단백질": 50, "지방": 53},
    "40대 남성 (30-49세)": {"칼로리": 2500, "탄수화물": 375, "단백질": 65, "지방": 69},
    "40대 여성 (30-49세)": {"칼로리": 1900, "탄수화물": 285, "단백질": 50, "지방": 53},
    "50대 남성 (50-64세)": {"칼로리": 2200, "탄수화물": 330, "단백질": 60, "지방": 61},
    "50대 여성 (50-64세)": {"칼로리": 1800, "탄수화물": 270, "단백질": 50, "지방": 50},
    "60대 이상 남성 (65세+)": {"칼로리": 2000, "탄수화물": 300, "단백질": 60, "지방": 55},
    "60대 이상 여성 (65세+)": {"칼로리": 1600, "탄수화물": 240, "단백질": 50, "지방": 44},
}

# ============================================================
# 목표별 식단 DB
# ============================================================
DIET_PLANS = {
    "🔥 다이어트 (체중 감량)": {
        "설명": "칼로리 제한 + 고단백 식단으로 체지방을 줄이는 식단",
        "칼로리_비율": 0.80,
        "아침": [
            {"음식": "오트밀", "양": "100g", "칼로리": 389, "탄수화물": 66, "단백질": 17, "지방": 7},
            {"음식": "삶은 계란", "양": "2개", "칼로리": 156, "탄수화물": 1, "단백질": 13, "지방": 11},
            {"음식": "저지방 우유", "양": "200ml", "칼로리": 68, "탄수화물": 10, "단백질": 7, "지방": 2},
        ],
        "점심": [
            {"음식": "닭가슴살 구이", "양": "150g", "칼로리": 247, "탄수화물": 0, "단백질": 46, "지방": 5},
            {"음식": "현미밥", "양": "150g", "칼로리": 218, "탄수화물": 46, "단백질": 4, "지방": 2},
            {"음식": "샐러드", "양": "200g", "칼로리": 35, "탄수화물": 7, "단백질": 2, "지방": 0},
        ],
        "저녁": [
            {"음식": "연어 구이", "양": "150g", "칼로리": 280, "탄수화물": 0, "단백질": 40, "지방": 13},
            {"음식": "고구마", "양": "100g", "칼로리": 86, "탄수화물": 20, "단백질": 2, "지방": 0},
            {"음식": "브로콜리 무침", "양": "150g", "칼로리": 51, "탄수화물": 10, "단백질": 4, "지방": 1},
        ],
        "간식": [
            {"음식": "그릭요거트", "양": "150g", "칼로리": 100, "탄수화물": 6, "단백질": 17, "지방": 1},
            {"음식": "아몬드", "양": "20g", "칼로리": 116, "탄수화물": 4, "단백질": 4, "지방": 10},
        ],
    },
    "💪 린매스업 (체지방 유지 + 근육 증가)": {
        "설명": "적절한 칼로리 잉여 + 고단백 식단으로 근육을 만드는 식단",
        "칼로리_비율": 1.10,
        "아침": [
            {"음식": "현미밥", "양": "200g", "칼로리": 290, "탄수화물": 61, "단백질": 6, "지방": 2},
            {"음식": "계란 스크램블", "양": "3개", "칼로리": 234, "탄수화물": 2, "단백질": 20, "지방": 16},
            {"음식": "바나나", "양": "1개", "칼로리": 89, "탄수화물": 23, "단백질": 1, "지방": 0},
        ],
        "점심": [
            {"음식": "닭가슴살 볶음밥", "양": "300g", "칼로리": 420, "탄수화물": 55, "단백질": 35, "지방": 8},
            {"음식": "된장국", "양": "1그릇", "칼로리": 50, "탄수화물": 5, "단백질": 4, "지방": 2},
            {"음식": "김치", "양": "100g", "칼로리": 18, "탄수화물": 4, "단백질": 1, "지방": 0},
        ],
        "저녁": [
            {"음식": "소고기 불고기", "양": "150g", "칼로리": 330, "탄수화물": 10, "단백질": 30, "지방": 18},
            {"음식": "흰쌀밥", "양": "200g", "칼로리": 260, "탄수화물": 57, "단백질": 5, "지방": 1},
            {"음식": "나물 반찬", "양": "150g", "칼로리": 80, "탄수화물": 10, "단백질": 3, "지방": 3},
        ],
        "간식": [
            {"음식": "단백질 쉐이크", "양": "1스쿱", "칼로리": 120, "탄수화물": 5, "단백질": 25, "지방": 2},
            {"음식": "고구마", "양": "150g", "칼로리": 130, "탄수화물": 30, "단백질": 3, "지방": 0},
        ],
    },
    "🥗 클린 벌크업 (깔끔하게 근육 증가)": {
        "설명": "고칼로리 + 고단백 식단으로 근육을 키우는 식단",
        "칼로리_비율": 1.20,
        "아침": [
            {"음식": "오트밀 + 바나나", "양": "200g", "칼로리": 320, "탄수화물": 60, "단백질": 10, "지방": 5},
            {"음식": "삶은 계란", "양": "3개", "칼로리": 234, "탄수화물": 2, "단백질": 20, "지방": 16},
            {"음식": "아몬드 버터", "양": "30g", "칼로리": 180, "탄수화물": 6, "단백질": 7, "지방": 16},
        ],
        "점심": [
            {"음식": "현미밥", "양": "300g", "칼로리": 435, "탄수화물": 92, "단백질": 9, "지방": 3},
            {"음식": "닭가슴살", "양": "200g", "칼로리": 330, "탄수화물": 0, "단백질": 62, "지방": 7},
            {"음식": "두부조림", "양": "150g", "칼로리": 120, "탄수화물": 5, "단백질": 12, "지방": 6},
        ],
        "저녁": [
            {"음식": "소고기 스테이크", "양": "200g", "칼로리": 440, "탄수화물": 0, "단백질": 46, "지방": 27},
            {"음식": "구운 감자", "양": "200g", "칼로리": 154, "탄수화물": 36, "단백질": 4, "지방": 0},
            {"음식": "시금치 무침", "양": "150g", "칼로리": 60, "탄수화물": 8, "단백질": 5, "지방": 2},
        ],
        "간식": [
            {"음식": "단백질 쉐이크", "양": "2스쿱", "칼로리": 240, "탄수화물": 10, "단백질": 50, "지방": 4},
            {"음식": "통밀빵 + 땅콩버터", "양": "2장", "칼로리": 280, "탄수화물": 30, "단백질": 12, "지방": 14},
        ],
    },
    "🍔 더티 벌크업 (빠르게 체중 + 근육 증가)": {
        "설명": "고칼로리 식단으로 체중과 근육을 빠르게 늘리는 식단",
        "칼로리_비율": 1.35,
        "아침": [
            {"음식": "흰쌀밥", "양": "300g", "칼로리": 390, "탄수화물": 85, "단백질": 7, "지방": 1},
            {"음식": "계란 프라이", "양": "3개", "칼로리": 280, "탄수화물": 1, "단백질": 19, "지방": 22},
            {"음식": "베이컨", "양": "50g", "칼로리": 218, "탄수화물": 0, "단백질": 15, "지방": 17},
        ],
        "점심": [
            {"음식": "돼지갈비", "양": "250g", "칼로리": 550, "탄수화물": 15, "단백질": 45, "지방": 35},
            {"음식": "흰쌀밥", "양": "300g", "칼로리": 390, "탄수화물": 85, "단백질": 7, "지방": 1},
            {"음식": "된장찌개", "양": "1그릇", "칼로리": 80, "탄수화물": 8, "단백질": 6, "지방": 3},
        ],
        "저녁": [
            {"음식": "삼겹살", "양": "200g", "칼로리": 620, "탄수화물": 0, "단백질": 36, "지방": 52},
            {"음식": "쌈밥", "양": "200g", "칼로리": 280, "탄수화물": 60, "단백질": 6, "지방": 1},
            {"음식": "순두부찌개", "양": "1그릇", "칼로리": 150, "탄수화물": 8, "단백질": 12, "지방": 7},
        ],
        "간식": [
            {"음식": "단백질 쉐이크 + 우유", "양": "1잔", "칼로리": 350, "탄수화물": 30, "단백질": 35, "지방": 10},
            {"음식": "빵 + 버터", "양": "2개", "칼로리": 320, "탄수화물": 45, "단백질": 8, "지방": 12},
        ],
    },
}

# ============================================================
# 나이/성별로 영양소 기준 자동 선택
# ============================================================
def get_nutrient_standard(age, gender):
    if age <= 18:
        age_group = "10대"
    elif age <= 29:
        age_group = "20대"
    elif age <= 39:
        age_group = "30대"
    elif age <= 49:
        age_group = "40대"
    elif age <= 64:
        age_group = "50대"
    else:
        age_group = "60대 이상"
    for k in NUTRIENT_STANDARDS:
        if k.startswith(age_group) and gender in k:
            return NUTRIENT_STANDARDS[k], k
    return NUTRIENT_STANDARDS["20대 남성 (19-29세)"], "20대 남성 (19-29세)"

# ============================================================
# BMR / TDEE 계산
# ============================================================
def calculate_tdee(gender, weight, height, age):
    if gender == "남성":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr * 1.375

# ============================================================
# 세션 상태 초기화
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "meal_foods" not in st.session_state:
    st.session_state.meal_foods = {"아침": [], "점심": [], "저녁": [], "간식": []}

# ============================================================
# 헤더
# ============================================================
st.markdown("""
<div class="title-box">
    <h1>🥗 식단 관리 프로그램</h1>
    <p>나의 식단을 분석하고, 목표에 맞는 맞춤 식단을 추천받아보세요</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 홈 화면
# ============================================================
if st.session_state.page == "home":
    st.markdown('<div class="section-title">📋 기본 정보 입력</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("나이", min_value=10, max_value=100, value=25, step=1)
        height = st.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
    with col2:
        gender = st.selectbox("성별", ["남성", "여성"])
        weight = st.number_input("체중 (kg)", min_value=20.0, max_value=200.0, value=65.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("다음 →"):
        st.session_state.user_info = {"나이": age, "성별": gender, "키": height, "체중": weight}
        st.session_state.page = "menu"
        st.rerun()

# ============================================================
# 메뉴 선택
# ============================================================
elif st.session_state.page == "menu":
    info = st.session_state.user_info
    st.markdown(f"""
    <div class="card">
        <b>👤 내 정보</b> &nbsp;&nbsp;
        나이: <b>{info['나이']}세</b> &nbsp;|&nbsp;
        성별: <b>{info['성별']}</b> &nbsp;|&nbsp;
        키: <b>{info['키']}cm</b> &nbsp;|&nbsp;
        체중: <b>{info['체중']}kg</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🎯 무엇을 도와드릴까요?</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:2rem;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
            <div style="font-size:3rem">📊</div>
            <div style="font-size:1.3rem;font-weight:700;margin:0.5rem 0">영양소 분석</div>
            <div style="color:#666;font-size:0.9rem">오늘 먹은 음식을 입력하고<br>나이대별 권장량과 비교해보세요</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("1️⃣ 영양소 분석 시작"):
            st.session_state.page = "analysis"
            st.session_state.meal_foods = {"아침": [], "점심": [], "저녁": [], "간식": []}
            st.rerun()
    with col2:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:2rem;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
            <div style="font-size:3rem">🍽️</div>
            <div style="font-size:1.3rem;font-weight:700;margin:0.5rem 0">식단 추천</div>
            <div style="color:#666;font-size:0.9rem">목표와 체성분을 입력하고<br>맞춤 식단을 추천받으세요</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("2️⃣ 식단 추천 시작"):
            st.session_state.page = "recommend_goal"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, _ = st.columns([1, 3])
    with col_back:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 뒤로"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 1번 - 영양소 분석
# ============================================================
elif st.session_state.page == "analysis":
    st.markdown('<div class="section-title">📊 오늘의 식단 입력</div>', unsafe_allow_html=True)
    
    # 검색 가능한 음식 목록 안내
    with st.expander("💡 검색 가능한 음식 목록 보기"):
        food_list = list(FOOD_DB.keys())
        cols = st.columns(4)
        for i, food in enumerate(food_list):
            cols[i % 4].write(f"• {food}")

    meal_icons = {"아침": "🌅", "점심": "☀️", "저녁": "🌙", "간식": "🍪"}

    for meal in ["아침", "점심", "저녁", "간식"]:
        with st.expander(f"{meal_icons[meal]} {meal}", expanded=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_food = st.text_input(f"음식 이름", key=f"input_{meal}", placeholder="예) 닭가슴살, 현미밥, 바나나")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"추가", key=f"add_{meal}"):
                    if new_food.strip():
                        result = search_food(new_food.strip())
                        if result:
                            st.session_state.meal_foods[meal].append(result)
                            st.success(f"✅ {result['음식명']} 추가됨!")
                        else:
                            st.error(f"❌ '{new_food}' 을 찾지 못했어요. 위 목록에서 확인해주세요!")
                        st.rerun()

            if st.session_state.meal_foods[meal]:
                food_df = pd.DataFrame(st.session_state.meal_foods[meal])
                food_df.columns = ["음식명", "칼로리(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)"]
                st.dataframe(food_df, use_container_width=True, hide_index=True)

                total = {
                    "칼로리": sum(f["칼로리"] for f in st.session_state.meal_foods[meal]),
                    "탄수화물": sum(f["탄수화물"] for f in st.session_state.meal_foods[meal]),
                    "단백질": sum(f["단백질"] for f in st.session_state.meal_foods[meal]),
                    "지방": sum(f["지방"] for f in st.session_state.meal_foods[meal]),
                }
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("칼로리", f"{total['칼로리']:.0f} kcal")
                c2.metric("탄수화물", f"{total['탄수화물']:.1f} g")
                c3.metric("단백질", f"{total['단백질']:.1f} g")
                c4.metric("지방", f"{total['지방']:.1f} g")

                if st.button(f"🗑️ {meal} 초기화", key=f"clear_{meal}"):
                    st.session_state.meal_foods[meal] = []
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📊 분석하기"):
            all_foods = []
            for meal_foods in st.session_state.meal_foods.values():
                all_foods.extend(meal_foods)

            if not all_foods:
                st.error("음식을 하나 이상 추가해주세요!")
            else:
                total_intake = {
                    "칼로리": sum(f["칼로리"] for f in all_foods),
                    "탄수화물": sum(f["탄수화물"] for f in all_foods),
                    "단백질": sum(f["단백질"] for f in all_foods),
                    "지방": sum(f["지방"] for f in all_foods),
                }
                info = st.session_state.user_info
                standard, standard_name = get_nutrient_standard(info["나이"], info["성별"])

                st.markdown("---")
                st.markdown(f'<div class="section-title">📈 영양소 분석 결과 ({standard_name} 기준)</div>', unsafe_allow_html=True)

                units = {"칼로리": "kcal", "탄수화물": "g", "단백질": "g", "지방": "g"}
                cols = st.columns(4)
                for i, nutrient in enumerate(["칼로리", "탄수화물", "단백질", "지방"]):
                    intake = total_intake[nutrient]
                    rec = standard[nutrient]
                    diff = intake - rec
                    delta_str = f"+{diff:.1f}{units[nutrient]}" if diff > 0 else f"{diff:.1f}{units[nutrient]}"
                    cols[i].metric(f"{nutrient} ({units[nutrient]})", f"{intake:.1f}", delta=delta_str, delta_color="inverse")

                # 그래프
                nutrients = ["칼로리", "탄수화물", "단백질", "지방"]
                colors = ["#66bb6a", "#42a5f5", "#ff7043", "#ffca28"]
                pct_values = []
                text_values = []
                for n in nutrients:
                    intake = total_intake[n]
                    rec = standard[n]
                    pct = min((intake / rec * 100), 150) if rec > 0 else 0
                    pct_values.append(pct)
                    text_values.append(f"{intake:.0f}{units[n]}<br>({pct:.0f}%)")

                fig = go.Figure()
                for i, n in enumerate(nutrients):
                    fig.add_trace(go.Bar(
                        name=n, x=[n], y=[pct_values[i]],
                        marker_color=colors[i],
                        text=text_values[i], textposition="outside",
                    ))
                fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="권장량 100%")
                fig.update_layout(
                    title="나이대별 권장량 대비 섭취율 (%)",
                    yaxis_title="섭취율 (%)", height=400,
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Noto Sans KR"), showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown('<div class="section-title">💬 영양소 피드백</div>', unsafe_allow_html=True)
                for nutrient in ["칼로리", "탄수화물", "단백질", "지방"]:
                    intake = total_intake[nutrient]
                    rec = standard[nutrient]
                    pct = intake / rec * 100 if rec > 0 else 0
                    unit = units[nutrient]
                    if pct < 80:
                        diff = rec - intake
                        st.error(f"⚠️ **{nutrient}** 부족! 권장량보다 {diff:.1f}{unit} 적게 섭취했어요. ({pct:.0f}%)")
                    elif pct > 120:
                        diff = intake - rec
                        st.warning(f"📈 **{nutrient}** 초과! 권장량보다 {diff:.1f}{unit} 더 섭취했어요. ({pct:.0f}%)")
                    else:
                        st.success(f"✅ **{nutrient}** 적정 범위! 권장량의 {pct:.0f}% 섭취했어요.")

    with col2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 뒤로"):
            st.session_state.page = "menu"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 2번 - 목표 선택
# ============================================================
elif st.session_state.page == "recommend_goal":
    st.markdown('<div class="section-title">🎯 목표 선택</div>', unsafe_allow_html=True)
    goal = st.radio("나의 목표를 선택해주세요", list(DIET_PLANS.keys()), index=0)
    st.info(f"📌 {DIET_PLANS[goal]['설명']}")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("다음 →"):
            st.session_state.goal = goal
            st.session_state.page = "recommend_body"
            st.rerun()
    with col2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 뒤로"):
            st.session_state.page = "menu"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 2번 - 체성분 입력
# ============================================================
elif st.session_state.page == "recommend_body":
    goal = st.session_state.get("goal", "🔥 다이어트 (체중 감량)")
    st.markdown(f'<div class="section-title">📊 체성분 입력 ({goal})</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        body_fat = st.number_input("체지방률 (%)", min_value=1.0, max_value=60.0, value=20.0, step=0.1)
    with col2:
        muscle_mass = st.number_input("근육량 (kg)", min_value=10.0, max_value=100.0, value=30.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚫 알레르기 / 못 먹는 음식</div>', unsafe_allow_html=True)
    allergy = st.text_input("알레르기 식품", placeholder="예) 견과류, 유제품, 갑각류")
    cant_eat = st.text_input("못 먹는 음식", placeholder="예) 고수, 오이, 버섯")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🍽️ 식단 추천받기"):
            st.session_state.body_info = {
                "체지방률": body_fat, "근육량": muscle_mass,
                "알레르기": allergy, "못먹는음식": cant_eat,
            }
            st.session_state.page = "recommend_result"
            st.rerun()
    with col2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 뒤로"):
            st.session_state.page = "recommend_goal"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 2번 - 식단 추천 결과
# ============================================================
elif st.session_state.page == "recommend_result":
    goal = st.session_state.get("goal", "🔥 다이어트 (체중 감량)")
    body_info = st.session_state.get("body_info", {})
    user_info = st.session_state.user_info
    plan = DIET_PLANS[goal]

    tdee = calculate_tdee(user_info["성별"], user_info["체중"], user_info["키"], user_info["나이"])
    target_calories = tdee * plan["칼로리_비율"]

    st.markdown(f'<div class="section-title">🍽️ 맞춤 식단 추천 결과</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("목표", goal[:5])
    col2.metric("목표 칼로리", f"{target_calories:.0f} kcal")
    col3.metric("체지방률", f"{body_info.get('체지방률', 0)}%")
    col4.metric("근육량", f"{body_info.get('근육량', 0)} kg")

    if body_info.get("알레르기") or body_info.get("못먹는음식"):
        st.warning(f"⚠️ 알레르기: {body_info.get('알레르기', '없음')} | 못 먹는 음식: {body_info.get('못먹는음식', '없음')} → 해당 식품은 직접 다른 식품으로 대체해주세요!")

    st.markdown("---")
    meal_icons = {"아침": "🌅", "점심": "☀️", "저녁": "🌙", "간식": "🍪"}
    total_cal = total_carb = total_prot = total_fat = 0

    for meal in ["아침", "점심", "저녁", "간식"]:
        foods = plan[meal]
        meal_cal = sum(f["칼로리"] for f in foods)
        meal_carb = sum(f["탄수화물"] for f in foods)
        meal_prot = sum(f["단백질"] for f in foods)
        meal_fat = sum(f["지방"] for f in foods)
        total_cal += meal_cal
        total_carb += meal_carb
        total_prot += meal_prot
        total_fat += meal_fat

        with st.expander(f"{meal_icons[meal]} {meal} — {meal_cal:.0f} kcal", expanded=True):
            food_df = pd.DataFrame(foods)
            food_df = food_df.rename(columns={"음식": "음식명", "양": "양", "칼로리": "칼로리(kcal)", "탄수화물": "탄수화물(g)", "단백질": "단백질(g)", "지방": "지방(g)"})
            st.dataframe(food_df, use_container_width=True, hide_index=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("칼로리", f"{meal_cal:.0f} kcal")
            c2.metric("탄수화물", f"{meal_carb:.0f} g")
            c3.metric("단백질", f"{meal_prot:.0f} g")
            c4.metric("지방", f"{meal_fat:.0f} g")

    st.markdown("---")
    st.markdown('<div class="section-title">📊 하루 합계</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 칼로리", f"{total_cal:.0f} kcal", f"목표 {target_calories:.0f} kcal")
    c2.metric("탄수화물", f"{total_carb:.0f} g")
    c3.metric("단백질", f"{total_prot:.0f} g")
    c4.metric("지방", f"{total_fat:.0f} g")

    fig = px.pie(
        values=[total_carb * 4, total_prot * 4, total_fat * 9],
        names=["탄수화물", "단백질", "지방"],
        color_discrete_sequence=["#66bb6a", "#42a5f5", "#ff7043"],
        title="탄단지 칼로리 비율"
    )
    fig.update_layout(font=dict(family="Noto Sans KR"), height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 다른 목표로 다시 추천받기"):
            st.session_state.page = "recommend_goal"
            st.rerun()
    with col2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 처음으로"):
            st.session_state.page = "menu"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
