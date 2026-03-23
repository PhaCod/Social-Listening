import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame):
    section_title(
        "Executive Overview",
        "Trang này cho lãnh đạo nhìn nhanh sức khỏe tổng thể fanpage: tăng trưởng, tương tác, doanh thu và hiệu quả chi tiêu.",
    )
    info_block(
        "Cách đọc nhanh",
        "Nếu interaction tăng nhưng virality thấp, nội dung chưa đủ mạnh để được chia sẻ rộng. "
        "Nếu discussion_rate giảm liên tục, nên ưu tiên format mở thảo luận.",
    )

    total_posts = len(df_posts)
    total_likes = int(df_posts["likes"].sum())
    total_comments = int(df_posts["total_comments"].sum())
    total_shares = int(df_posts["total_shares"].sum())
    total_interactions = int(df_posts["interaction_score"].sum())
    avg_discussion = float(df_posts["discussion_rate"].mean())
    avg_virality = float(df_posts["virality_rate"].mean())

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Posts", f"{total_posts:,}")
    m2.metric("Likes", f"{total_likes:,}")
    m3.metric("Comments", f"{total_comments:,}")
    m4.metric("Shares", f"{total_shares:,}")
    m5.metric("Avg discussion", f"{avg_discussion:.2%}")
    m6.metric("Avg virality", f"{avg_virality:.2%}")

    trend = (
        df_posts.assign(date=df_posts["timestamp"].dt.date)
        .groupby("date", as_index=False)
        .agg(
            likes=("likes", "sum"),
            comments=("total_comments", "sum"),
            shares=("total_shares", "sum"),
            interactions=("interaction_score", "sum"),
        )
    )
    fig_trend = px.line(
        trend,
        x="date",
        y=["likes", "comments", "shares", "interactions"],
        title="Hiệu suất fanpage theo thời gian",
        labels={"value": "Volume", "date": "Ngày"},
    )
    fig_trend.update_layout(legend_title_text="KPI", hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("### Top 15 bài theo hiệu suất tổng hợp")
    top = df_posts.nlargest(15, "interaction_score")[[
        "post_id",
        "timestamp",
        "content_pillar",
        "campaign_type",
        "topic",
        "post_type",
        "interaction_score",
        "likes",
        "total_comments",
        "total_shares",
        "discussion_rate",
        "virality_rate",
    ]]
    st.dataframe(top, use_container_width=True)

    interaction_trend = trend["interactions"].tail(7).mean() - trend["interactions"].head(7).mean() if len(trend) >= 14 else 0
    actions = []
    if avg_discussion < 0.08:
        actions.append("Tỷ lệ thảo luận thấp: tăng post dạng câu hỏi mở, poll, hoặc tranh luận 2 chiều.")
    if avg_virality < 0.06:
        actions.append("Tỷ lệ chia sẻ thấp: thử format checklist/tips ngắn và CTA 'share cho bạn bè'.")
    if interaction_trend < 0:
        actions.append("Interaction đang giảm: thử lịch đăng mới theo khung giờ vàng ở tab Audience và Timing.")
    if not actions:
        actions.append("Hiệu suất ổn định: giữ trục nội dung hiện tại và tăng tần suất ở pillar top hiệu quả.")

    strategy_block("Hành động đề xuất trong tuần", actions, tone="good" if interaction_trend >= 0 else "warn")
