import os
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Global KV Risk Scanner",
    page_icon="🌐",
    layout="wide",
)

SYSTEM_INSTRUCTION = """
당신은 D2C 글로벌 브랜드 캠페인의 키비주얼(KV) 리스크를 사전 검수하는 글로벌 브랜드 안전성 및 컴플라이언스 최고 전문가입니다.
사용자가 제출한 KV 이미지와 캠페인 맥락을 바탕으로, 아래 20대 글로벌 규범(Norms) 기준에 부합하는지 엄격하게 진단하십시오.

[검수 기준 20대 글로벌 규범]
1. Gender & Identity
2. Race, Ethnicity & Heritage
3. Sexual Orientation & LGBTQ+ Rights
4. Socioeconomic Status
5. Religion & Belief Systems
6. Ageism
7. Disability & Neurodiversity
8. Violence, Hate & Harassment
9. Language & Communication
10. Cultural Sensitivity & Local Context
11. Child & Adolescent Protection
12. Social & Disaster Sensitivity
13. Diversity, Equity & Inclusion (DEI)
14. Localization & Transcreation
15. Health, Wellness & Medical Claims
16. Environment & Sustainability (ESG)
17. Privacy & Data Ethics
18. Legal & Regulatory Compliance
19. Consumer Deception & Fairness
20. AI Ethics & Technology Representation

[평가 등급 체계]
- 🔴 Critical (전면 송출 불가 또는 법적 제재, 즉각적 보이콧 유발)
- 🟡 Moderate (문화적 오해 소지, 특정 권역용 베리에이션 분기 필요)
- 🟢 Acceptable (글로벌 스탠다드 부합)

[산출 리포트 포맷]
반드시 다음 구조로 명확하고 전문적인 한국어로 작성하십시오:
1. 비주얼 메타 감지 (인물 구성, 주요 오브젝트, 제스처, 텍스트, 색채 및 분위기 요약)
2. 종합 리스크 스코어 (🔴 / 🟡 / 🟢 중 택1 및 1문장 요약)
3. 세부 규범 위반 및 리스크 분석 (위반 또는 주의가 필요한 항목만 선별하여 기술)
   - 해당 규범명:
   - 시각적 근거:
   - 고위험 취약 권역: (예: MENA/중동, 북미, 서유럽, 동남아 등)
   - 예상되는 파장:
4. 액션 가이드라인 (Mitigation Plan)
   - 글로벌 단일 에셋 유지 시 수정 제안 (Global Safe Alternative)
   - 권역별 에셋 분기 제작 가이드 (Regional Localization Alternative)
"""

# 사이드바
with st.sidebar:
    st.title("🌐 Scanner Settings")
    default_api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API Key", value=default_api_key, type="password")
    
    st.markdown("---")
    st.subheader("🎯 타깃 권역")
    target_regions = st.multiselect(
        "집행 권역 선택",
        ["글로벌 공통", "북미 (NA)", "서유럽 (EU)", "중동/북아프리카 (MENA)", "동남아시아 (SEA)", "동아시아 (KR/JP/CN)", "중남미 (LATAM)"],
        default=["글로벌 공통"]
    )
    campaign_notes = st.text_area("캠페인 메모 (선택)", placeholder="예: 20대 타깃 글로벌 뷰티 D2C 론칭 키비주얼")

# 메인 UI
st.title("D2C Global Campaign KV Risk Scanner")
st.caption("글로벌 20대 규범 기반 비주얼 리스크 실시간 진단 도구")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("1. KV 이미지 업로드")
    uploaded_file = st.file_uploader("검수할 이미지 선택 (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 에셋", use_container_width=True)

with col2:
    st.subheader("2. 진단 결과")
    if uploaded_file:
        if st.button("🚀 리스크 진단 실행", type="primary", use_container_width=True):
            if not api_key:
                st.error("API 키가 설정되지 않았습니다. 좌측 메뉴에 API 키를 넣어주세요.")
            else:
                with st.spinner("20대 규범 및 권역별 민감도를 스캔 중입니다..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        [집행 타깃 권역]: {', '.join(target_regions)}
                        [캠페인 배경 메모]: {campaign_notes if campaign_notes else '없음'}
                        
                        첨부된 캠페인 키비주얼 이미지를 20대 글로벌 규범에 맞춰 검수하고 리포트를 작성하세요.
                        """
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[image, prompt],
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_INSTRUCTION,
                                temperature=0.2
                            )
                        )
                        st.session_state["result"] = response.text
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

    if "result" in st.session_state:
        st.markdown(st.session_state["result"])
        st.download_button("📄 리포트 다운로드 (MD)", st.session_state["result"], file_name="KV_Risk_Report.md")
    else:
        st.info("왼쪽에 이미지를 올리고 [리스크 진단 실행] 버튼을 눌러주세요.")
