import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.constants import POST_TYPES, SENTIMENTS, TOPICS
from analytics.ui import info_block, section_title, strategy_block


def _build_hot_posts_last_7_days(data: pd.DataFrame, top_n: int) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    ts_max = data["timestamp"].max().normalize()
    day_starts = pd.date_range(end=ts_max, periods=7, freq="D")

    rows = []
    for day_start in day_starts:
        day_end = day_start + pd.Timedelta(days=1)
        day_data = data[(data["timestamp"] >= day_start) & (data["timestamp"] < day_end)].copy()
        if day_data.empty:
            continue

        top_posts = day_data.sort_values("interaction_score", ascending=False).head(top_n)
        for rank, (_, row) in enumerate(top_posts.iterrows(), start=1):
            rows.append(
                {
                    "window_date": day_start.date(),
                    "window_label": day_start.strftime("%d/%m"),
                    "rank": rank,
                    "rank_label": f"Top {rank}",
                    "post_id": row["post_id"],
                    "timestamp": row["timestamp"],
                    "topic": row["topic"],
                    "post_type": row["post_type"],
                    "likes": row["likes"],
                    "total_comments": row["total_comments"],
                    "total_shares": row["total_shares"],
                    "interaction_score": row["interaction_score"],
                }
            )

    return pd.DataFrame(rows)


def render(df_posts: pd.DataFrame):
    section_title(
        "Content Performance",
        "So sánh hiệu suất từng nhóm nội dung để biết nên sản xuất gì nhiều hơn.",
    )
    info_block(
        "Mục tiêu DA Marketing",
        "Tìm content pillar vừa có engagement tốt, vừa tạo click và doanh thu cao. "
        "Đây là cơ sở để phân bổ kế hoạch nội dung tháng tới.",
    )

    c1, c2, c3, c4 = st.columns(4)
    topics = c1.multiselect("Topic", [t for t in TOPICS], default=[t for t in TOPICS])
    post_types = c2.multiselect("Post type", POST_TYPES, default=POST_TYPES)
    sentiments = c3.multiselect("Sentiment", SENTIMENTS, default=SENTIMENTS)
    min_interaction = c4.slider("Min interaction", 0, int(df_posts["interaction_score"].max()), 200)

    data = df_posts.copy()
    data = data[data["topic"].isin(topics)]
    data = data[data["post_type"].isin(post_types)]
    data = data[data["sentiment"].isin(sentiments)]
    data = data[data["interaction_score"] >= min_interaction]

    pillar_perf = (
        data.groupby("content_pillar", as_index=False)
        .agg(
            post_count=("post_id", "count"),
            avg_interaction=("interaction_score", "mean"),
            avg_discussion=("discussion_rate", "mean"),
            avg_virality=("virality_rate", "mean"),
        )
        .sort_values("avg_interaction", ascending=False)
    )

    fig_pillar = px.bar(
        pillar_perf,
        x="content_pillar",
        y="avg_interaction",
        color="avg_virality",
        title="Pillar nào đang hiệu quả nhất",
        labels={"avg_interaction": "Avg interaction score", "content_pillar": "Content pillar"},
    )
    st.plotly_chart(fig_pillar, use_container_width=True)

    fig_scatter = px.scatter(
        data,
        x="content_length",
        y="interaction_score",
        color="content_pillar",
        size="total_comments",
        hover_data=["post_id", "campaign_type", "post_type"],
        title="Độ dài content và interaction",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### Top bài hot theo khung 24h trong 7 ngày gần nhất")
    top_n = st.slider("Số bài top mỗi ngày (24h)", min_value=1, max_value=5, value=3, step=1)
    hot_df = _build_hot_posts_last_7_days(data, top_n=top_n)

    if hot_df.empty:
        st.info("Không đủ dữ liệu cho 7 ngày gần nhất trong bộ lọc hiện tại.")
    else:
        fig_hot = px.bar(
            hot_df,
            x="window_label",
            y="interaction_score",
            color="rank_label",
            barmode="group",
            hover_data=["post_id", "topic", "post_type", "likes", "total_comments", "total_shares"],
            title="Top bài hot 24h theo từng ngày (7 ngày gần nhất)",
            labels={
                "window_label": "Ngày",
                "interaction_score": "Interaction score",
                "rank_label": "Thứ hạng",
            },
        )
        st.plotly_chart(fig_hot, use_container_width=True)

        st.dataframe(
            hot_df[
                [
                    "window_date",
                    "rank",
                    "post_id",
                    "timestamp",
                    "topic",
                    "post_type",
                    "likes",
                    "total_comments",
                    "total_shares",
                    "interaction_score",
                ]
            ].sort_values(["window_date", "rank"], ascending=[False, True]),
            use_container_width=True,
        )

    st.markdown("### Drill-down bài viết")
    cols = [
        "post_id",
        "timestamp",
        "content_pillar",
        "post_type",
        "topic",
        "sentiment",
        "likes",
        "total_comments",
        "total_shares",
        "interaction_score",
        "discussion_rate",
        "virality_rate",
    ]
    st.dataframe(data[cols].sort_values("timestamp", ascending=False), use_container_width=True)

    top_pillar = pillar_perf.iloc[0]["content_pillar"] if not pillar_perf.empty else "N/A"
    weak_pillar = pillar_perf.iloc[-1]["content_pillar"] if len(pillar_perf) > 1 else "N/A"

    actions = [f"Scale pillar {top_pillar} lên thêm 20-30% số bài trong tuần tới."]
    if weak_pillar != "N/A":
        actions.append(f"Rà soát pillar {weak_pillar}: tối ưu hook 3 dòng đầu và CTA ra link.")

    high_len = data[data["content_length"] > data["content_length"].median()]
    low_len = data[data["content_length"] <= data["content_length"].median()]
    if len(high_len) and len(low_len):
        if high_len["interaction_score"].mean() > low_len["interaction_score"].mean():
            actions.append("Nội dung dài đang hiệu quả hơn: giữ storytelling dài cho nhóm topic chính.")
        else:
            actions.append("Nội dung ngắn đang hiệu quả hơn: đẩy format ngắn + visual mạnh để tăng tốc độ consume.")

    strategy_block("Hành động nội dung", actions, tone="good")
