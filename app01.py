import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 앱 기본 설정
st.set_page_config(page_title="AI 라면 영양 및 만성질환 스캐너", page_icon="🍜", layout="centered")

st.title("🍜 AI 라면 종합 건강 영향 분석기")
st.write("사진을 업로드하면 최신 구글 AI가 만성질환 위험도를 정밀 진단하여 파트별 구분 라인과 함께 색상별로 표기합니다.")

# 🌟 [보안 수정] 코드 내부에 진짜 키를 적지 않고, 스트림릿 서버에 숨겨둔 키를 불러옵니다.
if "GEMINI_API_KEY" in st.secrets:
    CRITICAL_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    # 스트림릿 관리자 화면에 키를 넣지 않았을 때를 대비한 임시 입력창
    CRITICAL_API_KEY = st.text_input("🔑 구글 API 키를 입력하세요 (Secrets 설정 권장)", type="password")

# 2. 사진 입력 방식 선택
upload_type = st.radio("사진 입력 방식 선택", ["📁 갤러리 업로드", "📷 직접 촬영"])

uploaded_file = None
if upload_type == "📁 갤러리 업로드":
    uploaded_file = st.file_uploader("라면 사진 파일을 선택하세요", type=["jpg", "jpeg", "png"], key="gallery_file")
else:
    uploaded_file = st.camera_input("라면 사진 촬영", key="camera_file")

# 3. 자동 분석 프로세스
if uploaded_file is not None:
    if not CRITICAL_API_KEY:
        st.error("❌ 작동을 위해 구글 API 키 설정이 필요합니다.")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 라면 사진", use_container_width=True)
        
        with st.status("🚀 구글 AI가 질환별 핵심 지표를 정밀 분석 중입니다...", expanded=True) as status:
            try:
                genai.configure(api_key=CRITICAL_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """
                제공된 라면 사진을 정밀 분석하여 다음 가이드라인을 단 하나도 누락하지 말고 한국어로 상세하게 답변하세요.
                반드시 제시된 서식 규칙과 구조를 엄격하게 준수하여 작성해야 정보가 누락되거나 정리가 흐트러지지 않습니다.

                [⚠️ 반드시 준수해야 할 시각 서식 규칙]
                1. **가장 중요**: 각 PART(PART 1 제외)가 시작되기 직전 줄에는 반드시 `---` 문법을 입력하여 시각적 구분 라인(구분선)을 그리세요.
                2. 글자 크기는 거대한 제목 크기(#, ##)를 절대 쓰지 마세요. 오직 일반 본문 크기로만 출력되게 하세요.
                3. 주요 파트 번호와 대제목(중요 부문)은 무조건 :red[**굵은 빨간색**] 문법으로 감싸세요. (예: :red[**PART 1. 🎯 AI 분석 정확도 진단**])
                4. 각 파트 내의 핵심 안내 단위 소제목(주글지)은 무조건 :blue[파란색] 문법으로 감싸세요. (예: :blue[간 수치 영향:])
                5. 세부 설명 내용(보조글씨)은 가독성을 위해 문장마다 줄바꿈을 자주 사용하여 정갈하게 작성하세요.
                6. 문장 중간이든 어디든 '위험'이라는 두 글자가 출현하면 100% 확률로 :red[**위험**] 문법을 적용하여 붉고 두껍게 만드세요.

                [📝 종합 리포트 필수 포함 내용 및 구조]

                :red[**PART 1. 🎯 AI 분석 정확도 진단**]
                - :blue[인식 정확도 점수]: 사진 판독 및 데이터베이스 매칭 신뢰도를 % 수치로 선명하게 제시하고 이유를 명시하세요.

                ---
                :red[**PART 2. 📊 정밀 영양성분 표**]
                - 식별된 라면의 영양 정보를 열량, 나트륨, 탄수화물, 당류, 지방, 포화지방, 트랜스지방, 콜레스테롤, 단백질 항목이 모두 들어간 마크다운 표(Table)로 한눈에 정리하세요.

                ---
                :red[**PART 3. 📋 상세 원재료명 및 알레르기 안내**]
                - :blue[소재지 및 제조사]: 제조 브랜드 이름
                - :blue[면 및 스프 성분 리스트]: 밀가루 원산지, 팜유, 정제염, 핵산계 조미료 성분 등을 구체적으로 나열하세요.
                - :blue[⚠️ 알레르기 유발 물질]: 포장지에 명시된 알레르기 정보(밀, 대두, 쇠고기 등)를 꼼꼼히 기록하세요.

                ---
                :red[**PART 4. 🩺 4대 만성 질환 영향 정밀 진단**]
                - :blue[🧪 간 수치 영향]: 고탄수화물 면발이 비알코올성 지방간 및 간 세포 손상 수치(AST/ALT) 상승에 미치는 의학적 인과관계를 설명하고 위험성을 경고하세요.
                - :blue[🩸 콜레스테롤 영향]: 유탕 가공 시 포함된 '팜유'의 높은 포화지방이 혈중 나쁜 LDL 콜레스테롤 및 중성지방을 축적시키는 원인을 명확하게 짚으세요.
                - :blue[🍬 당뇨(혈당) 영향]: 정제 밀가루가 유발하는 식후 급격한 혈당 스파이크 현상과 췌장 무리로 인한 인슐린 저항성 유발의 위험 요소를 적으세요.
                - :blue[🫀 심혈관 영향]: 과도한 분말스프 속 나트륨이 삼투압 현상으로 혈압을 올려 고혈압을 유발하고, 포화지방과 결합해 동맥경화, 뇌졸중, 심근경색으로 발전하는 메커니즘을 상세히 다루세요.

                ---
                :red[**PART 5. 🚨 종합 위험도 판정**]
                - :blue[위험 등급 진단]: 이 라면을 일상적으로 자주 섭취할 때 내 몸에 미치는 종합적인 해로움을 분석하여 [안전 / 주의 / 위험] 등급 중 하나로 명확히 판정하고 의학적 근거 요약글을 한 줄 붙이세요.

                ---
                :red[**PART 6. 💡 건강한 조리 대안 및 섭취 팁**]
                - :blue[영양학적 조리 가이드]: 면을 따로 끓여 삶은 물(기름기)을 완전히 버리는 법, 스프 계량 조절법, 칼륨이 풍부하여 나트륨 배출을 돕는 채소(파, 양파 등)를 추가해 먹는 팁을 꼼꼼히 리스트로 안내하세요.
                """
                
                response = model.generate_content(contents=[prompt, image])
                status.update(label="🎉 파트 분할 정밀 리포트 생성 완료!", state="complete", expanded=False)
                
                st.divider()
                st.markdown(response.text)
                
            except Exception as e:
                status.update(label="❌ 분석 중 오류가 발생했습니다.", state="error")
                st.error(f"에러 원인: {e}")
