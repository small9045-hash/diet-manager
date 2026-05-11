import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# ============================================================
# 페이지 기본 설정
# ============================================================
st.set_page_config(
    page_title="식단 관리 프로그램",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS 스타일
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .main {
        background-color: #f8faf8;
    }

    .stApp {
        background: linear-gradient(135deg, #f8faf8 0%, #e8f5e9 100%);
    }

    .title-box {
        background: linear-gradient(135deg, #2e7d32, #66bb6a);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(46,125,50,0.3);
    }

    .title-box h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }

    .title-box p {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    .menu-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        border: 2px solid transparent;
    }

    .menu-card:hover {
        border-color: #66bb6a;
        box-shadow: 0 4px 20px rgba(46,125,50,0.2);
        transform: translateY(-2px);
    }

    .meal-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2e7d32;
        margin-bottom: 0.5rem;
    }

    .nutrient-label {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.2rem;
    }

    .food-tag {
        display: inline-block;
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2e7d32, #66bb6a);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.3s;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1b5e20, #43a047);
        box-shadow: 0 4px 15px rgba(46,125,50,0.4);
        transform: translateY(-1px);
    }

    .back-btn > button {
        background: #f5f5f5 !important;
        color: #333 !important;
        box-shadow: none !important;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2e7d32;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e8f5e9;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stRadio"] label {
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 500;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 식품안전처 API 설정
# ============================================================
FOOD_API_KEY = ""  # ← 발급받은 키 여기에 입력!

# ============================================================
# 나이대별 1일 영양소 권장량 (한국인 영양소 섭취기준)
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
# 목표별 식단 DB (Claude API 없이 규칙 기반)
# ============================================================
DIET_PLANS = {
    "🔥 다이어트 (체중 감량)": {
        "설명": "칼로리 제한 + 고단백 식단으로 체지방을 줄이는 식단",
        "칼로리_비율": 0.80,
        "탄단지_비율": {"탄수화물": 40, "단백질": 40, "지방": 20},
        "아침": [
            {"음식": "오트밀", "양": "100g", "칼로리": 389, "탄수화물": 66, "단백질": 17, "지방": 7},
            {"음식": "삶은 계란", "양": "2개", "칼로리": 156, "탄수화물": 1, "단백질": 13, "지방": 11},
            {"음식": "저지방 우유", "양": "200ml", "칼로리": 68, "탄수화물": 10, "단백질": 7, "지방": 2},
        ],
        "점심": [
            {"음식": "닭가슴살 구이", "양": "150g", "칼로리": 247, "탄수화물": 0, "단백질": 46, "지방": 5},
            {"음식": "현미밥", "양": "150g", "칼로리": 218, "탄수화물": 46, "단백질": 4, "지방": 2},
            {"음식": "샐러드 (드레싱 제외)", "양": "200g", "칼로리": 35, "탄수화물": 7, "단백질": 2, "지방": 0},
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
        "탄단지_비율": {"탄수화물": 45, "단백질": 35, "지방": 20},
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
        "설명": "고칼로리 + 고단백 식단으로 빠르게 근육을 키우는 식단",
        "칼로리_비율": 1.20,
        "탄단지_비율": {"탄수화물": 50, "단백질": 30, "지방": 20},
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
        "설명": "고칼로리 식단으로 체중과 근육을 빠르게 늘리는 식단 (체지방도 다소 증가)",
        "칼로리_비율": 1.35,
        "탄단지_비율": {"탄수화물": 50, "단백질": 25, "지방": 25},
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
# 식품안전처 API 음식 검색 함수
# ============================================================
def search_food(food_name):
    """식품안전처 API로 음식 영양소 검색"""
    try:
        url = "http://api.data.go.kr/openapi/tn_pubr_public_nutri_food_info_api"
        params = {
            "serviceKey": FOOD_API_KEY,
            "pageNo": "1",
            "numOfRows": "5",
            "type": "json",
            "foodNm": food_name
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("response", {}).get("header", {}).get("resultCode") == "00":
            items = data["response"]["body"]["items"]
            if items:
                item = items[0]
                return {
                    "음식명": item.get("foodNm", food_name),
                    "칼로리": float(item.get("enerc", 0) or 0),
                    "탄수화물": float(item.get("chocdf", 0) or 0),
                    "단백질": float(item.get("prot", 0) or 0),
                    "지방": float(item.get("fatce", 0) or 0),
                }
        return None
    except:
        return None

# ============================================================
# 나이/성별로 영양소 기준 자동 선택
# ============================================================
def get_nutrient_standard(age, gender):
    if age < 13:
        age = 13
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

    key = f"{age_group} {gender}"
    for k in NUTRIENT_STANDARDS:
        if k.startswith(age_group) and gender in k:
            return NUTRIENT_STANDARDS[k], k
    return NUTRIENT_STANDARDS["20대 남성 (19-29세)"], "20대 남성 (19-29세)"

# ============================================================
# BMR / TDEE 계산 (Harris-Benedict)
# ============================================================
def calculate_tdee(gender, weight, height, age, activity=1.375):
    if gender == "남성":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr * activity

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
# 홈 화면 (기본 정보 입력)
# ============================================================
if st.session_state.page == "home":
    st.markdown('<div class="section-title">📋 기본 정보 입력</div>', unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("나이", min_value=10, max_value=100, value=25, step=1)
            height = st.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
        with col2:
            gender = st.selectbox("성별", ["남성", "여성"])
            weight = st.number_input("체중 (kg)", min_value=20.0, max_value=200.0, value=65.0, step=0.1)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("다음 →"):
        st.session_state.user_info = {
            "나이": age,
            "성별": gender,
            "키": height,
            "체중": weight,
        }
        st.session_state.page = "menu"
        st.rerun()

# ============================================================
# 메뉴 선택 화면
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
        <div class="menu-card">
            <div style="font-size:3rem">📊</div>
            <div style="font-size:1.3rem; font-weight:700; margin:0.5rem 0">영양소 분석</div>
            <div style="color:#666; font-size:0.9rem">오늘 먹은 음식을 입력하고<br>나이대별 권장량과 비교해보세요</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("1️⃣ 영양소 분석 시작"):
            st.session_state.page = "analysis"
            st.session_state.meal_foods = {"아침": [], "점심": [], "저녁": [], "간식": []}
            st.rerun()

    with col2:
        st.markdown("""
        <div class="menu-card">
            <div style="font-size:3rem">🍽️</div>
            <div style="font-size:1.3rem; font-weight:700; margin:0.5rem 0">식단 추천</div>
            <div style="color:#666; font-size:0.9rem">목표와 체성분을 입력하고<br>맞춤 식단을 추천받으세요</div>
        </div>
        """, unsafe_allow_html=True)
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
    st.markdown("각 끼니별로 드신 음식을 입력해주세요. 음식 이름으로 자동 검색됩니다.")

    meal_icons = {"아침": "🌅", "점심": "☀️", "저녁": "🌙", "간식": "🍪"}

    for meal in ["아침", "점심", "저녁", "간식"]:
        with st.expander(f"{meal_icons[meal]} {meal}", expanded=True):
            # 음식 입력
            col1, col2 = st.columns([3, 1])
            with col1:
                new_food = st.text_input(f"음식 이름", key=f"input_{meal}", placeholder="예) 닭가슴살, 현미밥, 바나나")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"추가", key=f"add_{meal}"):
                    if new_food.strip():
                        with st.spinner("검색 중..."):
                            result = search_food(new_food.strip())
                        if result:
                            st.session_state.meal_foods[meal].append(result)
                            st.success(f"✅ {result['음식명']} 추가됨!")
                        else:
                            # API 실패시 기본값으로 추가
                            st.session_state.meal_foods[meal].append({
                                "음식명": new_food.strip(),
                                "칼로리": 0, "탄수화물": 0, "단백질": 0, "지방": 0
                            })
                            st.warning(f"⚠️ API에서 '{new_food}' 영양소를 찾지 못했어요. 직접 수정해주세요.")
                        st.rerun()

            # 추가된 음식 목록
            if st.session_state.meal_foods[meal]:
                food_df = pd.DataFrame(st.session_state.meal_foods[meal])
                food_df.columns = ["음식명", "칼로리(kcal)", "탄수화물(g)", "단백질(g)", "지방(g)"]
                st.dataframe(food_df, use_container_width=True, hide_index=True)

                col_sum = st.columns(4)
                total = {
                    "칼로리": sum(f["칼로리"] for f in st.session_state.meal_foods[meal]),
                    "탄수화물": sum(f["탄수화물"] for f in st.session_state.meal_foods[meal]),
                    "단백질": sum(f["단백질"] for f in st.session_state.meal_foods[meal]),
                    "지방": sum(f["지방"] for f in st.session_state.meal_foods[meal]),
                }
                col_sum[0].metric("칼로리", f"{total['칼로리']:.0f} kcal")
                col_sum[1].metric("탄수화물", f"{total['탄수화물']:.1f} g")
                col_sum[2].metric("단백질", f"{total['단백질']:.1f} g")
                col_sum[3].metric("지방", f"{total['지방']:.1f} g")

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
                st.error("음식을 하나 이상 입력해주세요!")
            else:
                # 총 섭취량 계산
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

                # 메트릭 카드
                metrics = ["칼로리", "탄수화물", "단백질", "지방"]
                units = {"칼로리": "kcal", "탄수화물": "g", "단백질": "g", "지방": "g"}
                cols = st.columns(4)
                for i, nutrient in enumerate(metrics):
                    intake = total_intake[nutrient]
                    rec = standard[nutrient]
                    diff = intake - rec
                    delta_str = f"+{diff:.1f}{units[nutrient]}" if diff > 0 else f"{diff:.1f}{units[nutrient]}"
                    cols[i].metric(
                        f"{nutrient} ({units[nutrient]})",
                        f"{intake:.1f}",
                        delta=delta_str,
                        delta_color="inverse"
                    )

                # 그래프
                fig = go.Figure()
                colors_intake = ["#66bb6a", "#42a5f5", "#ff7043", "#ffca28"]
                colors_standard = ["#c8e6c9", "#bbdefb", "#ffccbc", "#fff9c4"]

                for i, nutrient in enumerate(metrics):
                    intake = total_intake[nutrient]
                    rec = standard[nutrient]
                    pct = min((intake / rec * 100), 150) if rec > 0 else 0

                    fig.add_trace(go.Bar(
                        name=f"{nutrient} 섭취량",
                        x=[nutrient],
                        y=[pct],
                        marker_color=colors_intake[i],
                        text=f"{intake:.0f}{units[nutrient]}<br>({pct:.0f}%)",
                        textposition="outside",
                        width=0.4,
                    ))

                fig.add_hline(y=100, line_dash="dash", line_color="red",
                              annotation_text="권장량 100%", annotation_position="right")

                fig.update_layout(
                    title="나이대별 권장량 대비 섭취율 (%)",
                    yaxis_title="섭취율 (%)",
                    barmode="group",
                    height=400,
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font=dict(family="Noto Sans KR"),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

                # 피드백
                st.markdown('<div class="section-title">💬 영양소 피드백</div>', unsafe_allow_html=True)
                for nutrient in metrics:
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

    goal = st.radio(
        "나의 목표를 선택해주세요",
        list(DIET_PLANS.keys()),
        index=0
    )

    # 목표 설명
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
# 2번 - 체성분 / 알레르기 입력
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
                "체지방률": body_fat,
                "근육량": muscle_mass,
                "알레르기": allergy,
                "못먹는음식": cant_eat,
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

    # TDEE 계산
    tdee = calculate_tdee(user_info["성별"], user_info["체중"], user_info["키"], user_info["나이"])
    target_calories = tdee * plan["칼로리_비율"]

    st.markdown(f'<div class="section-title">🍽️ 맞춤 식단 추천 결과</div>', unsafe_allow_html=True)

    # 요약 카드
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("목표", goal.split(" ")[0] + goal.split(" ")[1])
    col2.metric("목표 칼로리", f"{target_calories:.0f} kcal")
    col3.metric("체지방률", f"{body_info.get('체지방률', 0)}%")
    col4.metric("근육량", f"{body_info.get('근육량', 0)} kg")

    if body_info.get("알레르기") or body_info.get("못먹는음식"):
        st.warning(f"⚠️ 알레르기: {body_info.get('알레르기', '없음')} | 못 먹는 음식: {body_info.get('못먹는음식', '없음')} → 해당 식품은 직접 다른 식품으로 대체해주세요!")

    st.markdown("---")

    # 끼니별 식단
    meal_icons = {"아침": "🌅", "점심": "☀️", "저녁": "🌙", "간식": "🍪"}
    total_cal = 0
    total_carb = 0
    total_prot = 0
    total_fat = 0

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
            food_df = food_df.rename(columns={
                "음식": "음식명", "양": "양",
                "칼로리": "칼로리(kcal)", "탄수화물": "탄수화물(g)",
                "단백질": "단백질(g)", "지방": "지방(g)"
            })
            st.dataframe(food_df, use_container_width=True, hide_index=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("칼로리", f"{meal_cal:.0f} kcal")
            c2.metric("탄수화물", f"{meal_carb:.0f} g")
            c3.metric("단백질", f"{meal_prot:.0f} g")
            c4.metric("지방", f"{meal_fat:.0f} g")

    # 하루 합계
    st.markdown("---")
    st.markdown('<div class="section-title">📊 하루 합계</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 칼로리", f"{total_cal:.0f} kcal", f"목표 {target_calories:.0f} kcal")
    c2.metric("탄수화물", f"{total_carb:.0f} g")
    c3.metric("단백질", f"{total_prot:.0f} g")
    c4.metric("지방", f"{total_fat:.0f} g")

    # 탄단지 비율 파이차트
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
