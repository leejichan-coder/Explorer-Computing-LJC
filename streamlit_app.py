import pandas as pd
import streamlit as st


GOAL_TIPS = {
    "과제 진행": (
        "시작 장벽 낮추기",
        "해야 할 일을 가장 작은 한 단계로 쪼개고, 그 단계만 끝내 보세요.",
        "완료한 부분과 다음에 할 일을 한 줄씩 적어 두세요.",
    ),
    "시험 복습": (
        "기억에서 꺼내 보기",
        "자료를 덮고 핵심 개념 3개를 직접 설명한 뒤, 틀린 부분만 확인하세요.",
        "헷갈린 개념 하나를 다음 복습 목록에 추가하세요.",
    ),
    "휴식 회복": (
        "화면에서 잠시 벗어나기",
        "물 마시기, 가볍게 걷기, 조용히 앉아 있기 중 한 가지를 골라 보세요.",
        "다음 일정에 필요한 물건을 정리하며 마무리하세요.",
    ),
}


def build_plan(minutes, energy, goal, deadline):
    if minutes < 15:
        raise ValueError("공강 시간은 15분 이상이어야 합니다.")
    if energy not in ("낮음", "보통", "높음"):
        raise ValueError("올바른 에너지 수준을 선택하세요.")
    if goal not in GOAL_TIPS:
        raise ValueError("올바른 목표를 선택하세요.")

    preparation = min(5, max(2, minutes // 30))
    wrap_up = min(5, max(2, minutes // 30))
    available = minutes - preparation - wrap_up

    rest_ratio = {"낮음": 0.35, "보통": 0.24, "높음": 0.16}[energy]
    if goal == "휴식 회복":
        rest_ratio += 0.25
    elif deadline == "오늘":
        rest_ratio -= 0.04
    rest_ratio = max(0.10, min(0.70, rest_ratio))

    break_time = max(2, min(available - 2, round(available * rest_ratio)))
    main_time = available - break_time

    return [
        ("준비", preparation),
        ("핵심 활동", main_time),
        ("쉬기", break_time),
        ("마무리", wrap_up),
    ]


st.set_page_config(
    page_title="공강시간 실험실 | Campus Gap Lab",
    page_icon="⏳",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {
        padding: 2rem 2.3rem;
        border-radius: 22px;
        background: linear-gradient(125deg, #142f4f 0%, #24677b 58%, #2d8d84 100%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero .eyebrow {font-size: .85rem; letter-spacing: .14em; font-weight: 700; opacity: .85;}
    .hero h1 {color: white; font-size: 2.45rem; line-height: 1.2; margin: .45rem 0;}
    .hero p {font-size: 1.06rem; margin: .7rem 0 0; opacity: .95;}
    .step-title {font-weight: 700; color: #155e69; margin-bottom: .3rem;}
    </style>
    <div class="hero">
      <div class="eyebrow">CAMPUS GAP LAB · STUDENT TOOL</div>
      <h1>공강시간 실험실</h1>
      <p>비어 있는 시간을 무조건 채우지 말고, 오늘의 상태에 맞게 나누어 보세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("나에게 맞는 공강 계획 만들기")
st.caption("시간·에너지·목표를 선택하면 계획과 시간 배분이 바로 나타납니다. 계정이나 개인정보는 필요하지 않습니다.")

with st.form("planner_form"):
    left, middle, right = st.columns(3, gap="large")
    with left:
        minutes = st.slider("공강 시간", min_value=15, max_value=180, value=60, step=5, format="%d분")
        energy = st.selectbox("지금 에너지", ["낮음", "보통", "높음"], index=1)
    with middle:
        goal = st.selectbox("이번 공강의 목표", list(GOAL_TIPS), index=0)
        deadline = st.selectbox("마감 시점", ["오늘", "3일 이내", "이번 주", "여유 있음"], index=1)
    with right:
        task = st.text_input("지금 할 일 한 줄", value="다음 수업 핵심 개념 3개 정리")
        st.write(" ")
        st.form_submit_button("내 계획 만들기", type="primary", use_container_width=True)

plan = build_plan(minutes, energy, goal, deadline)
plan_data = pd.DataFrame(plan, columns=["단계", "시간(분)"])
tip_title, tip_main, tip_end = GOAL_TIPS[goal]
task_text = task.strip() or "작은 목표 하나 정하기"

st.divider()
st.subheader("오늘의 4단계 계획")
st.write(f"**내 목표:** {task_text}")

for index, (label, duration) in enumerate(plan, start=1):
    if label == "준비":
        detail = "필요한 자료를 열고, 알림을 잠시 꺼 두세요."
    elif label == "핵심 활동":
        detail = f"{tip_title}: {tip_main}"
    elif label == "쉬기":
        detail = "화면을 내려놓고 눈과 몸을 잠깐 쉬게 해 주세요."
    else:
        detail = tip_end
    st.markdown(f"**{index:02d} · {label} — {duration}분**")
    st.write(detail)

chart_col, summary_col = st.columns([1.4, 1], gap="large")
with chart_col:
    st.subheader("시간 배분")
    st.bar_chart(
        plan_data,
        x="단계",
        y="시간(분)",
        horizontal=True,
        sort=False,
        color="#238b8a",
        height=260,
    )
with summary_col:
    st.subheader("한눈에 보기")
    st.metric("총 공강 시간", f"{minutes}분")
    st.metric("핵심 활동", f"{plan[1][1]}분")
    st.metric("쉬는 시간", f"{plan[2][1]}분")
    st.info("에너지가 낮으면 휴식 비율이 늘고, 오늘 마감인 과제는 핵심 활동 비율이 조금 늘어납니다.")

download_text = "공강시간 실험실\n" + f"목표: {task_text}\n" + "\n".join(
    f"{label}: {duration}분" for label, duration in plan
)
st.download_button(
    "계획을 텍스트 파일로 저장",
    data=download_text,
    file_name="my_campus_gap_plan.txt",
    mime="text/plain",
)
st.caption("이 계획은 참고용입니다. 몸 상태와 실제 일정에 맞게 자유롭게 조정하세요.")
