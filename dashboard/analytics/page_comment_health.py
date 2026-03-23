import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame, df_comments: pd.DataFrame):
    section_title(
        "Comment Health",
        "Theo dõi sức khỏe thảo luận: cảm xúc comment, mức độ tương tác và tín hiệu nhiễu.",
    )
    info_block(
        "Mục tiêu DA Marketing",
        "Phát hiện sớm comment tiêu cực hoặc spam để team phản hồi đúng lúc, bảo vệ hình ảnh fanpage.",
    )

    comments = df_comments.copy()
    if "sentiment" not in comments.columns:
        comments["sentiment"] = pd.NA
    if "reactions" not in comments.columns:
        comments["reactions"] = 0
    if "is_noise_ui_text" not in comments.columns:
        comments["is_noise_ui_text"] = False

    post_meta = df_posts[["post_id", "content_pillar", "campaign_type", "topic", "sentiment"]].rename(
        columns={"sentiment": "post_sentiment"}
    )

    merged = comments.merge(
        post_meta,
        on="post_id",
        how="left",
    )
    merged["comment_sentiment"] = merged["sentiment"].fillna("Missing")

    sentiment_mix = (
        merged.groupby(["content_pillar", "comment_sentiment"], dropna=False)
        .size()
        .reset_index(name="count")
        .fillna("Missing")
    )

    fig_mix = px.bar(
        sentiment_mix,
        x="content_pillar",
        y="count",
        color="comment_sentiment",
        barmode="stack",
        title="Sentiment comment theo content pillar",
    )
    st.plotly_chart(fig_mix, use_container_width=True)

    top_threads = (
        merged.groupby("post_id", as_index=False)
        .agg(comment_count=("author", "count"), total_comment_reactions=("reactions", "sum"))
        .sort_values(["total_comment_reactions", "comment_count"], ascending=False)
        .head(20)
    )
    st.dataframe(top_threads, use_container_width=True)

    noise_rate = merged["is_noise_ui_text"].mean() if len(merged) else 0.0
    st.metric("UI text noise rate", f"{noise_rate:.2%}")

    neg_rate = (merged["comment_sentiment"] == "Tiêu cực").mean() if len(merged) else 0.0
    actions = []
    if neg_rate > 0.2:
        actions.append("Tăng tần suất phản hồi comment tiêu cực trong 2 giờ đầu sau đăng.")
    actions.append("Chuẩn hóa template phản hồi cho 3 nhóm: hỏi thông tin, phàn nàn, và góp ý.")
    if noise_rate > 0.05:
        actions.append("Ưu tiên xử lý parser comment vì tỷ lệ nhiễu UI đang cao.")

    strategy_block("Hành động quản trị cộng đồng", actions, tone="warn" if neg_rate > 0.2 else "good")
