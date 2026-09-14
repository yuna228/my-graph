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
    "많은 종류 중 한 영화를 선택하면, 하루 영화의 관객수를 날짜별로 "
    "선 그래프로 확인할 수 있다."
)

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

# ==================================================
# 그래프 3
# ==================================================
st.divider()
st.header("그래프 3. 날짜별 10위권 전체 일관객")

st.markdown(
    "각 날짜의 박스오피스 10위권 영화의 일관객을 모두 합산해 "
    "전체 영화 관객 규모가 시간에 따라 어떻게 변했는지 살펴봅니다."
)


# 날짜별 10위권 일관객 합계
daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)


# 일관객 합계가 가장 컸던 3일
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)


# 영역 그래프
fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 박스오피스 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    },
    hover_data={
        "날짜": "|%Y-%m-%d",
        "일관객": ":,.0f"
    }
)


# 마우스 오버
fig3.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,.0f}명"
        "<extra></extra>"
    )
)


# TOP 3 날짜를 그래프 위에 표시
for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"{row['날짜'].strftime('%Y-%m-%d')}"
            f"<br>{row['일관객']:,.0f}명"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-55,
        font=dict(size=12)
    )


fig3.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)",
    height=600
)


st.plotly_chart(
    fig3,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "날짜별로 극장가 전체의 관객 규모가 어떻게 변했는지와 "
    "특히 관객이 가장 많이 몰린 날이 언제였는지 확인할 수 있습니다."
)

# ==================================================
# 그래프 4
# ==================================================
st.divider()
st.header("그래프 4. 영화별 누적 일관객 TOP 10")

st.markdown(
    "이 기간 동안 각 영화의 일관객을 모두 더해 "
    "누적 관객이 많은 영화 10편을 비교합니다."
)


# 영화별 누적 일관객과 10위권 등장 일수 계산
movie_summary = (
    df.groupby("영화명")
    .agg(
        누적일관객=("일관객", "sum"),
        **{"10위권 등장 일수": ("날짜", "count")}
    )
    .reset_index()
)


# 누적 일관객 TOP 10
top10_movies = (
    movie_summary
    .sort_values("누적일관객", ascending=False)
    .head(10)
    .sort_values("누적일관객", ascending=True)
)


# 가로 막대그래프
fig4 = px.bar(
    top10_movies,
    x="누적일관객",
    y="영화명",
    orientation="h",
    title="기간 내 누적 일관객 TOP 10",
    labels={
        "누적일관객": "기간 내 일관객 합계",
        "영화명": "영화"
    },
    hover_data={
        "누적일관객": ":,.0f",
        "10위권 등장 일수": True
    }
)


# 마우스 오버 내용
fig4.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "기간 내 일관객 합계: %{x:,.0f}명<br>"
        "10위권 등장 일수: %{customdata[0]}일"
        "<extra></extra>"
    )
)


fig4.update_layout(
    xaxis_title="기간 내 일관객 합계(명)",
    yaxis_title="영화",
    height=600,
    yaxis=dict(
        categoryorder="total ascending"
    )
)


st.plotly_chart(
    fig4,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "이 기간 동안 어떤 영화가 가장 많은 관객을 모았는지와 "
    "각 영화가 박스오피스 10위권에 얼마나 오래 머물렀는지를 비교할 수 있습니다."
)
# ==================================================
# 그래프 5
# ==================================================
st.divider()
st.header("그래프 5. 월 × 요일별 일관객 히트맵")

st.markdown(
    "월과 요일에 따라 박스오피스 10위권의 일관객 합계가 "
    "어떻게 달라지는지 한눈에 살펴봅니다."
)


# 월과 요일 추출
heatmap_df = df.copy()

heatmap_df["월"] = heatmap_df["날짜"].dt.month

weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

heatmap_df["요일"] = heatmap_df["날짜"].dt.dayofweek.map(
    dict(enumerate(weekday_order))
)


# 월 × 요일별 일관객 합계
heatmap_data = (
    heatmap_df
    .pivot_table(
        index="월",
        columns="요일",
        values="일관객",
        aggfunc="sum",
        fill_value=0
    )
    .reindex(columns=weekday_order)
)


# 히트맵
fig5 = px.imshow(
    heatmap_data,
    text_auto=".3s",
    aspect="auto",
    color_continuous_scale="Blues",
    title="월 × 요일별 박스오피스 10위권 일관객 합계",
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    }
)


# 마우스 오버
fig5.update_traces(
    hovertemplate=(
        "%{y}월 %{x}<br>"
        "일관객 합계: %{z:,.0f}명"
        "<extra></extra>"
    )
)


fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    height=600,
    coloraxis_colorbar_title="일관객 합계"
)


st.plotly_chart(
    fig5,
    use_container_width=True
)


# 그래프로 알 수 있는 것
st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    "어떤 달의 어떤 요일에 박스오피스 10위권 영화들의 관객이 "
    "많이 몰렸는지 월과 요일의 패턴을 한눈에 비교할 수 있습니다."
)
