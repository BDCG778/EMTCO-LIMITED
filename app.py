import streamlit as st
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="항공 업무 통합 마스터 툴", layout="wide")
st.title("✈️ 항공 업무 통합 관리 시스템 (복구 완료)")

# 1. 엑셀 로드 함수 (오류 방지 강화)
@st.cache_data
def load_city_data():
    # 기본 공항 데이터 (엑셀이 안 읽힐 때를 대비한 비상용)
    default_cities = {
        "ICN": "인천", "GMP": "김포", "PUS": "김해", "CJU": "제주",
        "MWX": "무안", "YNY": "양양", "CJJ": "청주", "TAE": "대구",
        "DXB": "두바이", "CDG": "파리", "NRT": "나리타", "KIX": "오사카"
    }
    try:
        df = pd.read_excel("city_data.xlsx")
        df['code'] = df['code'].astype(str).str.upper().str.strip()
        excel_cities = dict(zip(df['code'], df['name']))
        default_cities.update(excel_cities) # 엑셀 데이터가 있으면 덮어쓰기
        return default_cities
    except:
        return default_cities # 엑셀 없으면 비상용 데이터로 작동

AIRLINES = {"KE": "대한항공", "OZ": "아시아나항공", "CZ": "중국남방항공", "QR": "카타르항공", "JL": "일본항공"}
CITIES = load_city_data()
MONTHS_KO = {"JAN": "1월", "FEB": "2월", "MAR": "3월", "APR": "4월", "MAY": "5월", "JUN": "6월", "JUL": "7월", "AUG": "8월", "SEP": "9월", "OCT": "10월", "NOV": "11월", "DEC": "12월"}

def calculate_day_change(d_str, a_str):
    months = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
    try:
        curr_yr = datetime.now().year
        d_obj = datetime(curr_yr, months[d_str[2:]], int(d_str[:2]))
        a_obj = datetime(curr_yr, months[a_str[2:]], int(a_str[:2]))
        diff = (a_obj - d_obj).days
        if diff < -300: 
            a_obj = datetime(curr_yr + 1, months[a_str[2:]], int(a_str[:2]))
            diff = (a_obj - d_obj).days
        return f" (+{diff})" if diff > 0 else ""
    except: return ""

tab1, tab2, tab3 = st.tabs(["종합 스케줄 정리", "승객 명단 정리", "출입국 규정 확인"])

with tab1:
    st.subheader("스케줄 변환 (안전 모드)")
    input_sch = st.text_area("스케줄을 입력하세요:", height=200, key="sch_repair")
    if st.button("즉시 변환") or input_sch:
        if input_sch:
            pattern = r"([A-Z]{2})\s*(\d{1,4})[A-Z]?\s+.*(\d{2}[A-Z]{3})\s+.*([A-Z]{6}).*\s+(\d{4})\s+(\d{4})\s+(\d{2}[A-Z]{3})?"
            eng_res, kor_res = [], []
            for line in input_sch.strip().split('\n'):
                match = re.search(pattern, line.strip())
                if match:
                    f_code, f_num, d_str, route, t1, t2, a_str = match.groups()
                    day_change = calculate_day_change(d_str, a_str) if a_str else ""
                    eng_res.append(f"{f_code} {f_num:<5} {d_str[:2]} {d_str[2:]:<5} {route[:3]}/{route[3:]:<6} {t1} - {t2}{day_change}")
                    al_name = AIRLINES.get(f_code, f_code)
                    m_ko = MONTHS_KO.get(d_str[2:], d_str[2:])
                    d_city = CITIES.get(route[:3], route[:3])
                    a_city = CITIES.get(route[3:], route[3:])
                    kor_res.append(f"{al_name} {f_num}편   {m_ko} {int(d_str[:2])}일   {d_city}/{a_city}   {t1} - {t2}{day_change}")
            if eng_res:
                col1, col2 = st.columns(2)
                with col1: st.info("영문"); st.code("\n".join(eng_res))
                with col2: st.success("한글 요약"); st.code("\n".join(kor_res))

with tab2:
    st.subheader("승객 명단 정리")
    # Surname/GivenNames MR/MS 규칙 준수 [cite: 2025-09-27]
    input_name = st.text_area("명단을 입력하세요:", height=200, key="name_repair")
    if input_name:
        name_pattern = r"(?:\d\.\d)?([A-Z]+)/([A-Z\s]+)\s+(MR|MS)"
        names = [f"{m[0]}/{m[1].strip()} {m[2]}" for m in re.findall(name_pattern, input_name)]
        if names: st.success(f"{len(names)}명 정리 완료"); st.code("\n".join(names))

with tab3:
    st.subheader("🌐 출입국 규정 확인")
    st.link_button("IATA 규정 조회", "https://www.iatatravelcentre.com/#-1")
