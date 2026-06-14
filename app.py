import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go
import requests

# ══════════════════════════════════════════════════════
# 데이터
# ══════════════════════════════════════════════════════

NUTRITION_STANDARDS = {
    "10대 (13~18세)": {
        "남": {"칼로리": 2700, "단백질": 65, "지방": 90, "탄수화물": 380, "칼슘": 900, "철분": 14, "비타민C": 100},
        "여": {"칼로리": 2000, "단백질": 55, "지방": 65, "탄수화물": 280, "칼슘": 900, "철분": 16, "비타민C": 100},
    },
    "20대 (19~29세)": {
        "남": {"칼로리": 2600, "단백질": 65, "지방": 85, "탄수화물": 360, "칼슘": 800, "철분": 10, "비타민C": 100},
        "여": {"칼로리": 2000, "단백질": 55, "지방": 65, "탄수화물": 280, "칼슘": 800, "철분": 14, "비타민C": 100},
    },
    "30대 (30~39세)": {
        "남": {"칼로리": 2500, "단백질": 65, "지방": 80, "탄수화물": 350, "칼슘": 800, "철분": 10, "비타민C": 100},
        "여": {"칼로리": 1900, "단백질": 55, "지방": 60, "탄수화물": 260, "칼슘": 800, "철분": 14, "비타민C": 100},
    },
    "40대 (40~49세)": {
        "남": {"칼로리": 2400, "단백질": 65, "지방": 80, "탄수화물": 330, "칼슘": 800, "철분": 10, "비타민C": 100},
        "여": {"칼로리": 1900, "단백질": 55, "지방": 60, "탄수화물": 260, "칼슘": 800, "철분": 14, "비타민C": 100},
    },
    "50대 이상 (50세~)": {
        "남": {"칼로리": 2200, "단백질": 60, "지방": 70, "탄수화물": 310, "칼슘": 800, "철분": 10, "비타민C": 100},
        "여": {"칼로리": 1800, "단백질": 50, "지방": 55, "탄수화물": 250, "칼슘": 800, "철분": 8,  "비타민C": 100},
    },
}

UNITS = {
    "칼로리": "kcal", "단백질": "g", "지방": "g",
    "탄수화물": "g", "칼슘": "mg", "철분": "mg", "비타민C": "mg",
}

DAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

ACTIVITY_LEVELS = {
    "거의 활동 없음 (좌식)":        1.2,
    "가벼운 운동 (주 1~3회)":       1.375,
    "보통 운동 (주 3~5회)":         1.55,
    "격렬한 운동 (주 6~7회)":       1.725,
    "매우 격렬 (하루 2회 운동 등)": 1.9,
}

BULK_MEALS = {
    "아침": [
        {"이름": "잡곡밥 2공기 + 계란 3개 스크램블 + 우유 500ml",    "칼로리": 850, "단백질": 45, "탄수화물": 110, "지방": 22},
        {"이름": "오트밀 200g + 바나나 2개 + 프로틴 셰이크",          "칼로리": 780, "단백질": 42, "탄수화물": 105, "지방": 14},
        {"이름": "현미밥 2공기 + 닭가슴살 200g + 고구마 200g",        "칼로리": 900, "단백질": 50, "탄수화물": 120, "지방": 10},
        {"이름": "통밀빵 4장 + 땅콩버터 + 삶은달걀 3개 + 우유",       "칼로리": 820, "단백질": 40, "탄수화물": 95,  "지방": 28},
        {"이름": "닭죽 대접 + 고구마 150g + 프로틴 셰이크",           "칼로리": 760, "단백질": 44, "탄수화물": 100, "지방": 12},
    ],
    "점심": [
        {"이름": "현미밥 2공기 + 제육볶음 + 된장국 + 반찬 3가지",     "칼로리": 1050, "단백질": 52, "탄수화물": 140, "지방": 28},
        {"이름": "닭갈비 + 잡곡밥 2공기 + 치즈 추가",                "칼로리": 1100, "단백질": 58, "탄수화물": 135, "지방": 30},
        {"이름": "스테이크 300g + 현미밥 + 구운채소",                 "칼로리": 980,  "단백질": 60, "탄수화물": 90,  "지방": 32},
        {"이름": "참치마요 주먹밥 3개 + 미역국 + 계란찜",             "칼로리": 900,  "단백질": 42, "탄수화물": 125, "지방": 20},
        {"이름": "소고기 볶음밥 + 된장찌개 + 나물반찬 2가지",         "칼로리": 1000, "단백질": 48, "탄수화물": 130, "지방": 26},
    ],
    "저녁": [
        {"이름": "연어 200g + 현미밥 + 아보카도 샐러드",              "칼로리": 820, "단백질": 48, "탄수화물": 85,  "지방": 30},
        {"이름": "닭가슴살 250g + 고구마 200g + 브로콜리",            "칼로리": 750, "단백질": 55, "탄수화물": 80,  "지방": 10},
        {"이름": "소고기 불고기 + 잡곡밥 2공기 + 두부조림",           "칼로리": 950, "단백질": 52, "탄수화물": 115, "지방": 24},
        {"이름": "닭볶음탕 + 현미밥 + 김치찌개",                     "칼로리": 880, "단백질": 50, "탄수화물": 100, "지방": 20},
        {"이름": "계란 4개 오믈렛 + 현미밥 + 토마토 샐러드",          "칼로리": 700, "단백질": 38, "탄수화물": 80,  "지방": 22},
    ],
    "간식": [
        {"이름": "프로틴 셰이크 + 바나나 2개",                       "칼로리": 380, "단백질": 30, "탄수화물": 55, "지방": 4},
        {"이름": "그릭요거트 200g + 견과류 30g + 꿀",                "칼로리": 350, "단백질": 18, "탄수화물": 35, "지방": 16},
        {"이름": "삶은달걀 3개 + 고구마 150g",                       "칼로리": 340, "단백질": 22, "탄수화물": 42, "지방": 12},
        {"이름": "땅콩버터 토스트 2장 + 우유 300ml",                 "칼로리": 420, "단백질": 18, "탄수화물": 48, "지방": 18},
    ],
}

LEAN_MEALS = {
    "아침": [
        {"이름": "잡곡밥 + 계란 2개 + 닭가슴살 100g + 된장국",       "칼로리": 580, "단백질": 42, "탄수화물": 68, "지방": 12},
        {"이름": "오트밀 150g + 블루베리 + 삶은달걀 2개 + 두유",     "칼로리": 520, "단백질": 30, "탄수화물": 70, "지방": 10},
        {"이름": "현미밥 + 두부부침 + 미역국 + 김치",               "칼로리": 550, "단백질": 28, "탄수화물": 72, "지방": 14},
        {"이름": "고구마 200g + 계란 3개 + 그릭요거트",              "칼로리": 540, "단백질": 34, "탄수화물": 65, "지방": 13},
        {"이름": "닭가슴살 죽 + 삶은달걀 + 견과류",                  "칼로리": 510, "단백질": 38, "탄수화물": 58, "지방": 12},
    ],
    "점심": [
        {"이름": "닭가슴살 200g + 현미밥 + 나물반찬 + 된장국",       "칼로리": 680, "단백질": 48, "탄수화물": 80, "지방": 12},
        {"이름": "연어 170g + 잡곡밥 + 채소 샐러드",                "칼로리": 650, "단백질": 42, "탄수화물": 72, "지방": 18},
        {"이름": "비빔밥 (닭가슴살 추가) + 미역국",                  "칼로리": 700, "단백질": 40, "탄수화물": 90, "지방": 14},
        {"이름": "두부 스테이크 + 현미밥 + 브로콜리볶음 + 된장국",   "칼로리": 620, "단백질": 36, "탄수화물": 78, "지방": 14},
        {"이름": "고등어구이 + 잡곡밥 + 시금치나물 + 김치찌개",      "칼로리": 660, "단백질": 44, "탄수화물": 75, "지방": 16},
    ],
    "저녁": [
        {"이름": "닭가슴살 200g + 고구마 150g + 샐러드",             "칼로리": 550, "단백질": 46, "탄수화물": 58, "지방": 8},
        {"이름": "소고기 안심 150g + 현미밥 + 구운채소",             "칼로리": 600, "단백질": 40, "탄수화물": 65, "지방": 16},
        {"이름": "순두부찌개 + 잡곡밥 + 나물반찬 2가지",             "칼로리": 530, "단백질": 30, "탄수화물": 68, "지방": 14},
        {"이름": "황태국 + 현미밥 + 두부조림 + 김치",               "칼로리": 560, "단백질": 38, "탄수화물": 62, "지방": 12},
        {"이름": "참치 샐러드 + 현미밥 + 된장국",                   "칼로리": 520, "단백질": 36, "탄수화물": 65, "지방": 10},
    ],
    "간식": [
        {"이름": "닭가슴살 바 + 아몬드 15알",                       "칼로리": 260, "단백질": 26, "탄수화물": 18, "지방": 10},
        {"이름": "그릭요거트 150g + 블루베리",                      "칼로리": 200, "단백질": 14, "탄수화물": 22, "지방": 4},
        {"이름": "삶은달걀 2개 + 방울토마토",                       "칼로리": 190, "단백질": 14, "탄수화물": 8,  "지방": 10},
        {"이름": "두유 300ml + 견과류 20g",                         "칼로리": 240, "단백질": 12, "탄수화물": 20, "지방": 12},
    ],
}

DIET_MEALS = {
    "아침": [
        {"이름": "오트밀 100g + 사과 + 삶은달걀 1개",               "칼로리": 360, "단백질": 18, "탄수화물": 58, "지방": 6},
        {"이름": "현미밥 2/3공기 + 미역국 + 두부조림",              "칼로리": 380, "단백질": 20, "탄수화물": 52, "지방": 8},
        {"이름": "고구마 150g + 그릭요거트 100g + 블루베리",         "칼로리": 340, "단백질": 14, "탄수화물": 58, "지방": 4},
        {"이름": "잡곡밥 2/3공기 + 된장국 + 나물반찬",              "칼로리": 370, "단백질": 16, "탄수화물": 60, "지방": 6},
        {"이름": "닭가슴살 샐러드 + 통밀빵 1장",                    "칼로리": 350, "단백질": 30, "탄수화물": 35, "지방": 8},
    ],
    "점심": [
        {"이름": "닭가슴살 150g + 현미밥 2/3공기 + 채소볶음",       "칼로리": 480, "단백질": 38, "탄수화물": 55, "지방": 8},
        {"이름": "야채비빔밥 (달걀 1개) + 된장국",                   "칼로리": 500, "단백질": 20, "탄수화물": 80, "지방": 10},
        {"이름": "두부 샐러드 + 현미밥 2/3공기 + 미역국",            "칼로리": 450, "단백질": 24, "탄수화물": 62, "지방": 10},
        {"이름": "고등어 100g + 잡곡밥 2/3공기 + 시금치나물",        "칼로리": 490, "단백질": 32, "탄수화물": 58, "지방": 12},
        {"이름": "닭가슴살 샐러드 볼 (드레싱 적게) + 현미밥",        "칼로리": 440, "단백질": 36, "탄수화물": 50, "지방": 8},
    ],
    "저녁": [
        {"이름": "닭가슴살 120g + 고구마 100g + 브로콜리",           "칼로리": 380, "단백질": 34, "탄수화물": 38, "지방": 6},
        {"이름": "두부찌개 + 현미밥 1/2공기 + 나물반찬",             "칼로리": 400, "단백질": 22, "탄수화물": 50, "지방": 10},
        {"이름": "참치 샐러드 + 오이 + 현미밥 1/2공기",              "칼로리": 360, "단백질": 28, "탄수화물": 44, "지방": 8},
        {"이름": "황태국 + 잡곡밥 1/2공기 + 김치",                  "칼로리": 350, "단백질": 26, "탄수화물": 42, "지방": 6},
        {"이름": "계란찜 + 현미밥 1/2공기 + 채소무침",               "칼로리": 370, "단백질": 20, "탄수화물": 48, "지방": 8},
    ],
    "간식": [
        {"이름": "방울토마토 + 오이 + 삶은달걀 1개",                "칼로리": 120, "단백질": 8,  "탄수화물": 10, "지방": 5},
        {"이름": "그릭요거트 100g + 키위 1개",                      "칼로리": 140, "단백질": 10, "탄수화물": 16, "지방": 2},
        {"이름": "견과류 15g + 사과 1/2개",                         "칼로리": 160, "단백질": 4,  "탄수화물": 18, "지방": 8},
        {"이름": "두유 200ml + 바나나 1/2개",                       "칼로리": 150, "단백질": 6,  "탄수화물": 24, "지방": 3},
    ],
}

GOAL_DB = {
    "💪 벌크업": ("벌크업", BULK_MEALS, 1.20, "단백질 35% / 탄수화물 45% / 지방 20%"),
    "🔥 린매스업": ("린매스업", LEAN_MEALS, 1.10, "단백질 40% / 탄수화물 40% / 지방 20%"),
    "🥗 다이어트": ("다이어트", DIET_MEALS, 0.80, "단백질 40% / 탄수화물 35% / 지방 25%"),
}

GOAL_TIPS = {
    "벌크업": [
        "운동 후 30분 이내에 단백질 + 탄수화물을 보충하세요.",
        "잠들기 전 카제인 단백질(코티지치즈, 그릭요거트)은 야간 근합성에 도움됩니다.",
        "체중 1kg당 1.6~2.2g의 단백질 섭취를 목표로 하세요.",
        "주 3~4회 이상 복합 운동(스쿼트, 데드리프트, 벤치프레스)을 병행하세요.",
    ],
    "린매스업": [
        "클린 푸드(현미, 닭가슴살, 고구마, 채소)를 중심으로 식단을 구성하세요.",
        "가공식품, 정제 탄수화물, 트랜스지방을 최대한 피하세요.",
        "체중 1kg당 1.8~2.2g의 단백질 + 공복 유산소를 병행하면 효과적입니다.",
        "수분 섭취를 하루 2L 이상 유지하세요.",
    ],
    "다이어트": [
        "식이섬유가 풍부한 채소를 매 끼니 곁들여 포만감을 높이세요.",
        "천천히 먹고 식사 시간은 최소 20분 이상 유지하세요.",
        "단백질을 충분히 섭취해야 근손실 없이 체지방만 줄일 수 있습니다.",
        "수면 7~8시간 유지와 스트레스 관리가 다이어트 성공의 핵심입니다.",
    ],
}


# ══════════════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════════════

def get_age_group(age):
    if age < 19:   return "10대 (13~18세)"
    elif age < 30: return "20대 (19~29세)"
    elif age < 40: return "30대 (30~39세)"
    elif age < 50: return "40대 (40~49세)"
    else:          return "50대 이상 (50세~)"

def calc_bmr(gender, weight, height, age):
    if gender == "남":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def status_label(ratio):
    if ratio < 60:     return "🔴 매우 부족"
    elif ratio < 80:   return "🟡 부족"
    elif ratio <= 120: return "🟢 적정"
    elif ratio <= 150: return "🟡 약간 과잉"
    else:              return "🔴 과잉"

def status_color(ratio):
    if ratio < 60:     return "#ef4444"
    elif ratio < 80:   return "#f59e0b"
    elif ratio <= 120: return "#22c55e"
    elif ratio <= 150: return "#f59e0b"
    else:              return "#ef4444"

def search_food(query):
    """식품의약품안전처 식품영양성분 API 검색"""
    try:
        api_key = st.secrets["API_KEY"]
        url = "https://apis.data.go.kr/1471000/FoodNtrCpntDbInfo02/getFoodNtrCpntDbInq02"
        params = {
            "serviceKey": api_key,
            "pageNo": 1,
            "numOfRows": 10,
            "type": "json",
            "FOOD_NM_KR": query,
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        items = data.get("body", {}).get("items", [])
        return items if items else []
    except Exception as e:
        return []


# ══════════════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════════════

st.set_page_config(page_title="🥗 식단 관리 프로그램", page_icon="🥗", layout="wide")

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(135deg, #2e7d32, #66bb6a);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .option-card {
        background: #f0fdf4; border-radius: 16px;
        padding: 2.5rem; text-align: center;
        border: 2px solid #bbf7d0; margin-bottom: 1rem;
    }
    .option-icon { font-size: 3.5rem; }
    .option-title { font-size: 1.4rem; font-weight: 700; margin: 0.6rem 0 0.3rem; }
    .option-desc { color: #6b7280; font-size: 0.9rem; line-height: 1.5; }
    .metric-box {
        background: #f0fdf4; border-radius: 12px;
        padding: 1rem; text-align: center; border: 1px solid #bbf7d0;
    }
    .metric-val { font-size: 1.6rem; font-weight: 700; color: #15803d; }
    .metric-label { font-size: 0.8rem; color: #6b7280; margin-top: 0.2rem; }
    .food-result {
        background: #f8fafc; border-radius: 10px;
        padding: 0.7rem 1rem; margin-bottom: 0.4rem;
        border-left: 4px solid #4ade80; cursor: pointer;
    }
    .meal-card {
        background: #f8fafc; border-radius: 10px;
        padding: 0.8rem 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #4ade80;
    }
    .meal-name { font-weight: 600; color: #1f2937; }
    .meal-info { font-size: 0.82rem; color: #6b7280; margin-top: 0.2rem; }
    .tip-box {
        background: #fffbeb; border-radius: 10px;
        padding: 0.7rem 1rem; margin-bottom: 0.4rem;
        border-left: 3px solid #fbbf24; font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🥗 식단 관리 프로그램</div>', unsafe_allow_html=True)
st.markdown("**개인 맞춤 영양 분석 & 목표별 일주일 식단 생성**")
st.divider()

# ══════════════════════════════════════════════════════
# 옵션 선택 화면
# ══════════════════════════════════════════════════════

if "option" not in st.session_state:
    st.session_state.option = None
if "foods" not in st.session_state:
    st.session_state.foods = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []

if st.session_state.option is None:
    st.markdown("## 원하는 기능을 선택하세요")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="option-card">
            <div class="option-icon">📊</div>
            <div class="option-title">옵션 1. 영양소 분석</div>
            <div class="option-desc">음식 이름을 검색하면<br>칼로리/영양소가 자동으로 입력되고<br>개인 맞춤 권장량과 비교 분석해드려요</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 옵션 1 선택", use_container_width=True, type="primary"):
            st.session_state.option = 1
            st.rerun()
    with col2:
        st.markdown("""
        <div class="option-card">
            <div class="option-icon">🗓️</div>
            <div class="option-title">옵션 2. 일주일 식단 생성</div>
            <div class="option-desc">목표(벌크업/린매스업/다이어트)와<br>신체 정보를 입력하면<br>맞춤 일주일 식단을 생성해드려요</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗓️ 옵션 2 선택", use_container_width=True, type="primary"):
            st.session_state.option = 2
            st.rerun()
    st.stop()

if st.button("← 처음으로 돌아가기"):
    st.session_state.option = None
    st.session_state.foods = []
    st.session_state.search_results = []
    st.rerun()

st.divider()

# ══════════════════════════════════════════════════════
# 옵션 1: 영양소 분석 (API 연동)
# ══════════════════════════════════════════════════════

if st.session_state.option == 1:
    st.subheader("📊 옵션 1 : 하루 섭취 영양소 분석")
    st.caption("음식 이름을 검색하면 칼로리/영양소가 자동으로 입력됩니다.")

    with st.expander("👤 기본 정보 입력", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            age1 = st.number_input("나이 (세)", 10, 90, 25, key="age1")
        with c2:
            gender1 = st.radio("성별", ["남", "여"], horizontal=True, key="gen1")
        with c3:
            weight1 = st.number_input("체중 (kg)", 30.0, 200.0, 70.0, key="wt1")
        with c4:
            height1 = st.number_input("키 (cm)", 100.0, 220.0, 170.0, key="ht1")
        activity1 = st.selectbox("활동량", list(ACTIVITY_LEVELS.keys()), index=2, key="act1")

    bmr1  = calc_bmr(gender1, weight1, height1, age1)
    tdee1 = bmr1 * ACTIVITY_LEVELS[activity1]
    age_group1 = get_age_group(age1)
    standard1 = NUTRITION_STANDARDS[age_group1][gender1].copy()
    standard1["칼로리"] = round(tdee1)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{bmr1:.0f}</div><div class="metric-label">기초대사량 BMR (kcal)</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{tdee1:.0f}</div><div class="metric-label">활동대사량 TDEE (kcal)</div></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{round(tdee1)}</div><div class="metric-label">오늘 권장 칼로리 (kcal)</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🍽️ 음식 검색 & 추가")

    # 음식 검색
    sc1, sc2 = st.columns([4, 1])
    with sc1:
        search_query = st.text_input("음식 이름 검색", placeholder="예: 잡곡밥, 닭가슴살, 바나나")
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 검색", use_container_width=True)

    if search_btn and search_query:
        with st.spinner("검색 중..."):
            results = search_food(search_query)
            st.session_state.search_results = results

    # 검색 결과 표시
    if st.session_state.search_results:
        st.markdown("**검색 결과** (추가할 음식 선택)")
        for i, item in enumerate(st.session_state.search_results):
            name  = item.get("FOOD_NM_KR", "")
            cal   = float(item.get("ENGY", 0) or 0)
            prot  = float(item.get("PROT", 0) or 0)
            fat   = float(item.get("FAT", 0) or 0)
            carb  = float(item.get("CHOCDF", 0) or 0)
            calc  = float(item.get("CA", 0) or 0)
            iron  = float(item.get("FE", 0) or 0)
            vitc  = float(item.get("VITC", 0) or 0)

            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                <div class="food-result">
                    <b>{name}</b><br>
                    <span style="font-size:0.82rem; color:#6b7280;">
                    칼로리 {cal:.0f}kcal | 단백질 {prot:.1f}g | 탄수화물 {carb:.1f}g | 지방 {fat:.1f}g
                    </span>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("➕ 추가", key=f"add_{i}"):
                    st.session_state.foods.append({
                        "이름": name,
                        "칼로리": cal, "단백질": prot, "지방": fat,
                        "탄수화물": carb, "칼슘": calc, "철분": iron, "비타민C": vitc,
                    })
                    st.success(f"'{name}' 추가됨!")
                    st.rerun()
    elif search_btn and search_query:
        st.warning("검색 결과가 없습니다. 다른 이름으로 검색해보세요.")

    # 추가된 음식 목록
    if st.session_state.foods:
        st.divider()
        st.markdown("**오늘 먹은 음식 목록**")
        df_foods = pd.DataFrame(st.session_state.foods)
        st.dataframe(df_foods, use_container_width=True, hide_index=True)

        # 합계 표시
        total = {k: sum(f[k] for f in st.session_state.foods)
                 for k in ["칼로리", "단백질", "지방", "탄수화물", "칼슘", "철분", "비타민C"]}

        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{total["칼로리"]:.0f}</div><div class="metric-label">총 칼로리 (kcal)</div></div>', unsafe_allow_html=True)
        with t2:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{total["단백질"]:.1f}</div><div class="metric-label">총 단백질 (g)</div></div>', unsafe_allow_html=True)
        with t3:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{total["탄수화물"]:.1f}</div><div class="metric-label">총 탄수화물 (g)</div></div>', unsafe_allow_html=True)
        with t4:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{total["지방"]:.1f}</div><div class="metric-label">총 지방 (g)</div></div>', unsafe_allow_html=True)

        if st.button("🗑️ 전체 초기화"):
            st.session_state.foods = []
            st.rerun()

        st.divider()
        st.subheader("📋 분석 결과")

        rows = []
        for nutrient, unit in UNITS.items():
            intake    = total[nutrient]
            recommend = standard1[nutrient]
            ratio     = intake / recommend * 100
            rows.append({
                "영양소": nutrient,
                "섭취량": f"{intake:.1f} {unit}",
                "권장량": f"{recommend} {unit}",
                "달성률": f"{ratio:.1f}%",
                "상태": status_label(ratio),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        nutrients = list(UNITS.keys())
        ratios    = [total[n] / standard1[n] * 100 for n in nutrients]
        colors    = [status_color(r) for r in ratios]
        fig = go.Figure(go.Bar(
            x=nutrients, y=ratios, marker_color=colors,
            text=[f"{r:.0f}%" for r in ratios], textposition="outside",
        ))
        fig.add_hline(y=100, line_dash="dash", line_color="#9ca3af", annotation_text="권장량 100%")
        fig.update_layout(title="영양소 달성률 (%)", yaxis_title="%",
                          height=380, plot_bgcolor="white", yaxis=dict(gridcolor="#f3f4f6"))
        st.plotly_chart(fig, use_container_width=True)

        mac_cal = total["단백질"]*4 + total["지방"]*9 + total["탄수화물"]*4
        if mac_cal > 0:
            fig2 = go.Figure(go.Pie(
                labels=["단백질", "지방", "탄수화물"],
                values=[total["단백질"]*4, total["지방"]*9, total["탄수화물"]*4],
                hole=0.45, marker_colors=["#4ade80", "#fb923c", "#60a5fa"],
            ))
            fig2.update_layout(title="칼로리 매크로 비율", height=320)
            st.plotly_chart(fig2, use_container_width=True)

        cal_remain = round(tdee1) - total["칼로리"]
        if cal_remain > 0:
            st.info(f"🔋 오늘 남은 칼로리 여유: **{cal_remain:.0f} kcal**")
        elif cal_remain < 0:
            st.warning(f"⚠️ 오늘 칼로리 초과: **{abs(cal_remain):.0f} kcal** 초과")
        else:
            st.success("✅ 오늘 칼로리를 딱 맞게 섭취했습니다!")
    else:
        st.info("음식을 검색해서 추가하면 분석 결과가 여기에 표시됩니다.")

# ══════════════════════════════════════════════════════
# 옵션 2: 일주일 식단 생성
# ══════════════════════════════════════════════════════

elif st.session_state.option == 2:
    st.subheader("🗓️ 옵션 2 : 목표 맞춤 일주일 식단 생성")

    with st.expander("👤 기본 정보 입력", expanded=True):
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            age2 = st.number_input("나이 (세)", 10, 90, 25, key="age2")
        with d2:
            gender2 = st.radio("성별", ["남", "여"], horizontal=True, key="gen2")
        with d3:
            weight2 = st.number_input("체중 (kg)", 30.0, 200.0, 70.0, key="wt2")
        with d4:
            height2 = st.number_input("키 (cm)", 100.0, 220.0, 170.0, key="ht2")
        activity2 = st.selectbox("활동량", list(ACTIVITY_LEVELS.keys()), index=2, key="act2")
        goal_key  = st.radio("목표", list(GOAL_DB.keys()), horizontal=True)

    if st.button("🗓️ 일주일 식단 생성", type="primary", use_container_width=True):
        goal_name, meal_db, cal_ratio, macro_guide = GOAL_DB[goal_key]
        bmr2       = calc_bmr(gender2, weight2, height2, age2)
        tdee2      = bmr2 * ACTIVITY_LEVELS[activity2]
        target_cal = tdee2 * cal_ratio

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{bmr2:.0f}</div><div class="metric-label">BMR (kcal)</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{tdee2:.0f}</div><div class="metric-label">TDEE (kcal)</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{target_cal:.0f}</div><div class="metric-label">목표 칼로리 (kcal)</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-box"><div class="metric-val">{goal_name}</div><div class="metric-label">선택 목표</div></div>', unsafe_allow_html=True)

        st.caption(f"권장 매크로 비율: {macro_guide}")
        st.divider()

        weekly = {"칼로리": 0, "단백질": 0, "탄수화물": 0, "지방": 0}
        used   = {mt: [] for mt in ["아침", "점심", "저녁", "간식"]}
        day_cals = []

        for day in DAYS:
            st.markdown(f"#### 📅 {day}")
            cols = st.columns(4)
            day_total = {"칼로리": 0, "단백질": 0, "탄수화물": 0, "지방": 0}

            for i, mt in enumerate(["아침", "점심", "저녁", "간식"]):
                pool = meal_db[mt]
                if len(used[mt]) >= len(pool):
                    used[mt] = []
                remaining = [m for m in pool if m["이름"] not in used[mt]]
                chosen = random.choice(remaining)
                used[mt].append(chosen["이름"])

                with cols[i]:
                    st.markdown(f"""
                    <div class="meal-card">
                        <div class="meal-name">[{mt}]<br>{chosen['이름']}</div>
                        <div class="meal-info">
                            🔥 {chosen['칼로리']}kcal<br>
                            단백질 {chosen['단백질']}g · 탄수 {chosen['탄수화물']}g · 지방 {chosen['지방']}g
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                for k in day_total:
                    day_total[k] += chosen[k]
                    weekly[k]    += chosen[k]

            diff = day_total["칼로리"] - target_cal
            diff_str = f"+{diff:.0f}" if diff >= 0 else f"{diff:.0f}"
            st.caption(f"하루 합계 → {day_total['칼로리']}kcal ({diff_str} vs 목표) | 단백질 {day_total['단백질']}g | 탄수화물 {day_total['탄수화물']}g | 지방 {day_total['지방']}g")
            day_cals.append(day_total["칼로리"])
            st.divider()

        st.subheader("📈 주간 요약")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("총 칼로리", f"{weekly['칼로리']:,} kcal", f"일 평균 {weekly['칼로리']/7:.0f} kcal")
        with s2:
            st.metric("총 단백질", f"{weekly['단백질']:,} g", f"일 평균 {weekly['단백질']/7:.0f} g")
        with s3:
            st.metric("총 탄수화물", f"{weekly['탄수화물']:,} g", f"일 평균 {weekly['탄수화물']/7:.0f} g")
        with s4:
            st.metric("총 지방", f"{weekly['지방']:,} g", f"일 평균 {weekly['지방']/7:.0f} g")

        fig3 = go.Figure(go.Bar(
            x=DAYS, y=day_cals, marker_color="#4ade80",
            text=[f"{c}kcal" for c in day_cals], textposition="outside",
        ))
        fig3.add_hline(y=target_cal, line_dash="dash", line_color="#ef4444",
                       annotation_text=f"목표 {target_cal:.0f}kcal")
        fig3.update_layout(title="요일별 칼로리", yaxis_title="kcal",
                           height=350, plot_bgcolor="white", yaxis=dict(gridcolor="#f3f4f6"))
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader(f"💪 {goal_name} 추가 팁")
        for tip in GOAL_TIPS[goal_name]:
            st.markdown(f'<div class="tip-box">• {tip}</div>', unsafe_allow_html=True)
