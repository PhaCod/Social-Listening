import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame, df_comments: pd.DataFrame):
    section_title(
        "Data Quality QA",
        "Đảm bảo dashboard đáng tin bằng cách theo dõi lỗi dữ liệu crawler và parser.",
    )
    info_block(
        "Vì sao quan trọng",
        "Nếu dữ liệu sai, mọi quyết định marketing phía sau đều sai. Trang này là lớp kiểm soát trước khi dùng KPI cho chiến lược.",
    )

    qa = df_posts.copy()
    qa["missing_topic"] = qa["topic"].isna()
    qa["missing_sentiment"] = qa["sentiment"].isna()
    qa["invalid_source_url"] = ~qa["source_url"].str.startswith("http", na=False)
    qa["short_content"] = qa["content"].str.len() < 40
    qa["suspected_post_comment_mix"] = qa["is_suspected_post_comment_mix"]
    qa["qa_error_count"] = qa[
        ["missing_topic", "missing_sentiment", "invalid_source_url", "short_content", "suspected_post_comment_mix"]
    ].sum(axis=1)

    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Missing topic", int(qa["missing_topic"].sum()))
    q2.metric("Missing sentiment", int(qa["missing_sentiment"].sum()))
    q3.metric("Invalid source_url", int(qa["invalid_source_url"].sum()))
    q4.metric("Short content", int(qa["short_content"].sum()))
    q5.metric("Post/comment mix", int(qa["suspected_post_comment_mix"].sum()))

    fig = px.histogram(qa, x="qa_error_count", nbins=6, title="Phân phối lỗi QA per post")
    st.plotly_chart(fig, use_container_width=True)

    noise_rate = float(df_comments["is_noise_ui_text"].mean()) if len(df_comments) else 0.0
    st.info(f"Tỷ lệ UI noise trong comment: {noise_rate:.2%}")

    total_checks = len(qa) * 5
    failed_checks = int(qa["qa_error_count"].sum())
    quality_score = 1 - (failed_checks / max(total_checks, 1))
    st.metric("Data quality score", f"{quality_score:.1%}")

    st.dataframe(
        qa[
            [
                "post_id",
                "timestamp",
                "content_pillar",
                "topic",
                "sentiment",
                "source_url",
                "missing_topic",
                "missing_sentiment",
                "invalid_source_url",
                "short_content",
                "suspected_post_comment_mix",
                "qa_error_count",
            ]
        ].sort_values("qa_error_count", ascending=False),
        use_container_width=True,
    )

    actions = []
    if quality_score < 0.9:
        actions.append("Khoanh vùng nguồn lỗi chính, ưu tiên sửa parser trước khi mở rộng campaign automation.")
    if qa["suspected_post_comment_mix"].sum() > 0:
        actions.append("Áp rule tách vùng post/comment rõ hơn để giảm nhầm lẫn nội dung.")
    if qa["invalid_source_url"].sum() > 0:
        actions.append("Bổ sung kiểm tra source_url bắt buộc để tăng khả năng trace bài gốc.")
    if not actions:
        actions.append("Chất lượng dữ liệu ổn, có thể dùng cho báo cáo tuần và dự báo nhẹ.")

    strategy_block("Hành động chất lượng dữ liệu", actions, tone="warn" if quality_score < 0.9 else "good")
