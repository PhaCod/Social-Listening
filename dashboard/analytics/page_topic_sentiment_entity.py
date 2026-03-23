import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame, df_entities: pd.DataFrame):
    section_title(
        "Topic, Sentiment và Entity",
        "Hiểu khách hàng đang quan tâm gì, phản ứng ra sao và entity nào mang lại giá trị kinh doanh.",
    )
    info_block(
        "Mục tiêu DA Marketing",
        "Từ topic và entity hiệu quả, xây content plan theo cụm nội dung có chuyển đổi cao.",
    )

    matrix = (
        df_posts.groupby(["topic", "sentiment"], dropna=False)
        .size()
        .reset_index(name="count")
        .fillna("Missing")
    )
    fig_matrix = px.bar(
        matrix,
        x="topic",
        y="count",
        color="sentiment",
        barmode="stack",
        title="Ma trận topic x sentiment",
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

    if df_entities.empty:
        st.info("Chưa có entities.")
        return

    top_entities = (
        df_entities.groupby(["entity_type", "entity_value"], as_index=False)
        .agg(
            mention_count=("post_id", "count"),
            avg_interaction=("interaction_score", "mean"),
            avg_virality=("virality_rate", "mean"),
            positive_rate=("post_sentiment", lambda s: (s == "Tích cực").mean()),
        )
        .sort_values("mention_count", ascending=False)
        .head(30)
    )

    fig_entity = px.scatter(
        top_entities,
        x="mention_count",
        y="avg_interaction",
        color="entity_type",
        size="positive_rate",
        hover_name="entity_value",
        title="Entity nào kéo tương tác tốt",
    )
    st.plotly_chart(fig_entity, use_container_width=True)

    st.dataframe(top_entities, use_container_width=True)

    actions = []
    top_topic = matrix.sort_values("count", ascending=False).iloc[0]["topic"] if not matrix.empty else "N/A"
    actions.append(f"Tăng tần suất nội dung quanh topic {top_topic} trong tuần tới.")

    best_entity = top_entities.sort_values("avg_interaction", ascending=False).head(1)
    if not best_entity.empty:
        entity_name = best_entity.iloc[0]["entity_value"]
        actions.append(f"Đẩy mini-series liên quan entity {entity_name} vì đang có interaction trung bình cao.")

    risk_negative = matrix[matrix["sentiment"].astype(str).str.contains("Tiêu cực", na=False)]["count"].sum()
    if risk_negative > 0:
        actions.append("Thiết kế post xử lý phản hồi tiêu cực và FAQ để giảm khủng hoảng cảm xúc.")

    strategy_block("Hành động theo topic/entity", actions, tone="good")
