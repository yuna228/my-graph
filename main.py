import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜형으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 열 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")

st.write(
    "1년치 일별 박스오피스 데이터를 이용해 "
    "영화의 관객 수가 시간에 따라 어떻게 변했는지 살펴봅니다."
)


# --------------------------------------------------
# 데이터 기본 정보
# --------------------------------------------------
st.caption(
    f"데이터 기간: {df['날짜'].min().strftime('%Y-%m-%d')} ~ "
    f"{df['날짜'].max().strftime('%Y-%m-%d')} · "
    f"총 {len(df):,}개 기록"
)


# ==================================================
# 그래프 1
# ==================================================
st.divider()
st.header("그래프 1. 영화별 일관객 변화")

st.markdown(
    "영화를 하나 선택하면 해당 영화의 **날짜별 일관객 수 변화**를 "
    "선 그래프로 확인할 수 있습니다."
)


# 영화 목록
movie_list = (
    df["영화명"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)


# 선택한 영화 데이터
movie_df = (
    df[df["영화명"] == selected_movie]
    .groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)


# 그래프
fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,.0f"
    }
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,.0f}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "영화의 일관객 수가 날짜에 따라 어떻게 증가하거나 감소하는지 "
    "확인할 수 있습니다."
)

# ==================================================
# 추가 그래프 구역
# ==================================================
st.divider()
st.header("그래프 3. 다음 그래프")

st.info("여기에 또 다른 그래프를 추가할 예정입니다.")

# ==================================================
# 그래프 2
# ==================================================
st.divider()
st.header("그래프 2. 일관객 합계 TOP 5 영화의 시간별 변화")

st.markdown(
    "이 기간 동안 **일관객 합계가 가장 큰 영화 5편**을 골라 "
    "날짜별 일관객 변화를 한 그래프에서 비교합니다."
)


# 기간 내 일관객 합계가 가장 큰 영화 5편 선정
top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)
)

top5_movie_names = top5_movies["영화명"].tolist()


# TOP 5 영화의 날짜별 데이터
top5_df = df[df["영화명"].isin(top5_movie_names)].copy()

top5_daily = (
    top5_df.groupby(["날짜", "영화명"], as_index=False)["일관객"]
    .sum()
    .sort_values(["날짜", "영화명"])
)


# 그래프
fig2 = px.line(
    top5_daily,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "영화명": True,
        "일관객": ":,.0f"
    }
)

fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}<br>"
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    hovermode="closest",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=600,
    legend_title="영화",
)


st.plotly_chart(
    fig2,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "기간 동안 가장 많은 관객을 모은 영화 5편의 흥행 규모와 "
    "날짜에 따른 관객 수 변화를 서로 비교할 수 있습니다."
)
