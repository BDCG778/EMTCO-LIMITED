import streamlit as st
import re
from datetime import datetime

st.set_page_config(page_title="항공 업무 통합 마스터 툴", layout="wide")
st.title("✈️ 항공 업무 통합 관리 시스템")

tab1, tab2, tab3 = st.tabs(["종합 스케줄 정리", "승객 명단 정리", "출입국 규정 확인"])

# --- [여기서부터 자유롭게 추가하세요!] ---
AIRLINES = {
    "KE": "대한항공", "OZ": "아시아나항공", "AF": "에어프랑스", "QR": "카타르항공", 
    "CX": "캐세이퍼시픽", "SQ": "싱가포르항공", "CZ": "중국남방항공", "MU": "중국동방항공", 
    "CA": "중국국제항공", "DL": "델타항공", "UA": "유나이티드항공", "AA": "아메리칸항공",
    "EK": "에미레이트항공", "EY": "에티하드항공", "AY": "핀에어", "LH": "루프트한자",
    "BA": "영국항공", "JL": "일본항공", "NH": "전일본공수", "VN": "베트남항공",
    "BR": "에바항공", "CI": "중화항공", "TK": "터키항공", "KL": "네덜란드항공"
}

CITIES = {
    # 한국 & 일본 & 중국
    "ICN": "인천", "GMP": "김포", "PUS": "부산", "CJU": "제주",
    "NRT": "나리타", "HND": "하네다", "KIX": "오사카", "FUK": "후쿠오카", "CTS": "삿포로",
    "PEK": "베이징", "PVG": "상하이", "CAN": "광저우", "HKG": "홍콩", "MFM": "마카오",
    # 동남아시아
    "BKK": "방콕", "SGN": "호치민", "HAN": "하노이", "DAD": "다낭", "SIN": "싱가포르",
    "MNL": "마닐라", "CEB": "세부", "CGK": "자카르타", "DPS": "발리", "KUL": "쿠알라룸푸르",
    # 미주 & 유럽 & 중동
    "LAX": "로스앤젤레스", "JFK": "뉴욕", "SFO": "샌프란시스코", "SEA": "시애틀", "YVR": "밴쿠버",
    "LHR": "런던", "CDG": "파리", "FRA": "프랑크푸르트", "AMS": "암스테르담", "FCO": "로마",
    "DXB": "두바이", "DOH": "도하", "AUH": "아부다비", "IST": "이스탄불", "DED": "데라둔"
}
# ----------------------------------------

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
    st.subheader("스케줄 변환 (한글 확장팩 적용)")
    input_sch = st.text_area("스케줄을 입력하세요:", height=250, key="sch_v_final")
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
                month_ko = MONTHS_KO.get(d_str[2:], d_str[2:])
                dep_city = CITIES.get(route[:3], route[:3])
                arr_city = CITIES.get(route[3:], route[3:])
                kor_results.append(f"{al_name} {f_num}편   {month_ko} {int(d_str[:2])}일   {dep_city}/{arr_city}   {t1} - {t2}{day_change}")

        if eng_results:
            st.success("변환 성공!")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**[영문 스케줄]**")
                st.code("\n".join(eng_results))
            with col2:
                st.write("**[한글 스케줄 요약]**")
                st.code("\n".join(kor_results))

with tab2:
    st.subheader("승객 명단 정리")
    st.info("Surname/GivenNames MR/MS 형식으로 자동 변환합니다.")
    input_name = st.text_area("명단을 입력하세요:", height=200, key="name_v_final")
    if input_name:
        # 사용자 정의 명단 규칙 준수 [cite: 2025-09-27]
        name_pattern = r"(?:\d\.\d)?([A-Z]+)/([A-Z\s]+)\s+(MR|MS)"
        names = [f"{m[0]}/{m[1].strip()} {m[2]}" for m in re.findall(name_pattern, input_name)]
        if names: st.success(f"{len(names)}명 정리 완료"); st.code("\n".join(names))

with tab3:
    st.subheader("🌐 출입국 규정 확인")
    st.link_button("IATA Your Journey 규정 조회하기", "https://www.iatatravelcentre.com/#-1")
