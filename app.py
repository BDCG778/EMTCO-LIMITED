import streamlit as st
import re
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="항공 업무 통합 마스터 툴", layout="wide")
st.title("✈️ 항공 업무 통합 관리 시스템")

tab1, tab2, tab3 = st.tabs(["종합 스케줄 정리", "승객 명단 정리", "출입국 규정 확인"])

# 엑셀에서 공항 데이터 로드
@st.cache_data
def load_city_data():
    try:
        # city_data.xlsx 파일을 읽어 딕셔너리로 변환
        df = pd.read_excel("city_data.xlsx")
        return dict(zip(df['code'], df['name']))
    except Exception as e:
        # 파일이 없거나 오류 시 기본값 출력
        return {"ICN": "인천", "DXB": "두바이"}

# 항공사 이름은 자주 쓰는 것만 코드에 유지 (필요시 수정)
AIRLINES = {"KE": "대한항공", "OZ": "아시아나항공", "CZ": "중국남방항공", "QR": "카타르항공", "AF": "에어프랑스"}
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

with tab1:
    st.subheader("스케줄 변환 (엑셀 공항 데이터 적용)")
    input_sch = st.text_area("스케줄을 입력하세요:", height=200, key="sch_v_excel")
    btn_convert = st.button("즉시 변환")
    
    if btn_convert or input_sch:
        pattern = r"([A-Z]{2})\s*(\d{1,4})[A-Z]?\s+.*(\d{2}[A-Z]{3})\s+.*([A-Z]{6}).*\s+(\d{4})\s+(\d{4})\s+(\d{2}[A-Z]{3})?"
        eng_results, kor_results = [], []
        for line in input_sch.strip().split('\n'):
            match = re.search(pattern, line.strip())
            if match:
                f_code, f_num, d_str, route, t1, t2, a_str = match.groups()
                day_change = calculate_day_change(d_str, a_str) if a_str else ""
                eng_results.append(f"{f_code} {f_num:<5} {d_str[:2]} {d_str[2:]:<5} {route[:3]}/{route[3:]:<6} {t1} - {t2}{day_change}")
                
                al_name = AIRLINES.get(f_code, f_code)
                m_ko = MONTHS_KO.get(d_str[2:], d_str[2:])
                d_city = CITIES.get(route[:3], route[:3])
                a_city = CITIES.get(route[3:], route[3:])
                kor_results.append(f"{al_name} {f_num}편   {m_ko} {int(d_str[:2])}일   {d_city}/{a_city}   {t1} - {t2}{day_change}")

        if eng_results:
            col1, col2 = st.columns(2)
            with col1: st.write("**[영문]**"); st.code("\n".join(eng_results))
            with col2: st.write("**[한글 요약]**"); st.code("\n".join(kor_results))

with tab2:
    st.subheader("승객 명단 정리")
    input_name = st.text_area("명단을 입력하세요:", height=200, key="name_v_excel")
    if input_name:
        # Surname/GivenNames MR/MS 형식 준수
        name_pattern = r"(?:\d\.\d)?([A-Z]+)/([A-Z\s]+)\s+(MR|MS)"
        names = [f"{m[0]}/{m[1].strip()} {m[2]}" for m in re.findall(name_pattern, input_name)]
        if names: st.success("정리 완료"); st.code("\n".join(names))

with tab3:
    st.subheader("🌐 출입국 규정 확인")
    st.link_button("IATA Your Journey 규정 조회하기", "https://www.iatatravelcentre.com/#-1")
