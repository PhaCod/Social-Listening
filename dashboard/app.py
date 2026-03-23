import streamlit as st

from analytics.mock_data import build_mock_data
from analytics.page_audience_timing import render as render_audience_timing
from analytics.page_campaign_roi import render as render_campaign_roi
from analytics.page_comment_health import render as render_comment_health
from analytics.page_content_performance import render as render_content_performance
from analytics.page_data_quality import render as render_data_quality
from analytics.page_funnel_conversion import render as render_funnel_conversion
from analytics.page_overview import render as render_overview
from analytics.page_topic_sentiment_entity import render as render_topic_sentiment_entity

st.set_page_config(page_title="Thánh Riviu Marketing Analytics", page_icon="📈", layout="wide")


def apply_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at 20% 0%, rgba(2,132,199,0.12), transparent 30%),
                        radial-gradient(circle at 80% 20%, rgba(251,191,36,0.10), transparent 28%),
                        #020617;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.2);
        }
        [data-testid="stSidebar"] * {
            color: #e5e7eb !important;
        }
        [data-testid="stSidebar"] .stRadio > label {
            font-weight: 600;
            color: #cbd5e1 !important;
            letter-spacing: 0.2px;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 10px;
            padding: 8px 10px;
            margin: 4px 0;
            background: rgba(15, 23, 42, 0.35);
            transition: all .15s ease-in-out;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            border-color: rgba(34, 211, 238, 0.55);
            background: rgba(30, 41, 59, 0.6);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            border-color: rgba(56, 189, 248, 0.95);
            background: rgba(2, 132, 199, 0.24);
            box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.3);
        }
        .stApp h1 {
            letter-spacing: 0.2px;
            font-weight: 800;
        }
        [data-testid="stMetric"] {
            border: 1px solid rgba(148,163,184,.24);
            border-radius: 12px;
            padding: 8px 10px;
            background: rgba(15,23,42,.28);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    apply_custom_style()
    st.title("Thánh Riviu Performance Dashboard")
    st.caption("Mock data cho DA Marketing - theo dõi hiệu suất content, funnel, conversion, campaign ROI và chất lượng dữ liệu crawler.")
    st.info(
        "Mỗi trang đều có 3 phần: 1) Ý nghĩa chỉ số, 2) Biểu đồ chính, 3) Hành động đề xuất. "
        "Bạn có thể dùng trực tiếp để họp chiến lược nội dung và campaign."
    )

    with st.sidebar:
        st.markdown("### Điều hướng")
        page = st.radio(
            "Chọn tab",
            [
                "Executive Overview",
                "Content Performance",
                "Funnel và Conversion",
                "Audience và Timing",
                "Topic, Sentiment và Entity",
                "Campaign Benchmark",
                "Comment Health",
                "Data Quality QA",
            ],
        )

        st.markdown("### Mock settings")
        seed = st.number_input("Random seed", min_value=1, max_value=99_999_999, value=20260323, step=1)
        n_posts = st.slider("Số lượng posts", min_value=80, max_value=600, value=240, step=20)

    df_posts, df_comments, df_entities = build_mock_data(seed=int(seed), n_posts=int(n_posts))

    with st.sidebar:
        st.markdown("### Bộ lọc thời gian")
        min_date = df_posts["timestamp"].min().date()
        max_date = df_posts["timestamp"].max().date()
        selected_range = st.date_input(
            "Khoảng ngày",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date = end_date = selected_range

    mask = (df_posts["timestamp"].dt.date >= start_date) & (df_posts["timestamp"].dt.date <= end_date)
    df_posts = df_posts[mask].copy()

    post_ids = set(df_posts["post_id"].tolist())
    df_comments = df_comments[df_comments["post_id"].isin(post_ids)].copy()
    df_entities = df_entities[df_entities["post_id"].isin(post_ids)].copy()

    if df_posts.empty:
        st.warning("Không có dữ liệu trong khoảng ngày đã chọn. Hãy mở rộng bộ lọc thời gian ở sidebar.")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Posts", f"{len(df_posts):,}")
    m2.metric("Comments", f"{len(df_comments):,}")
    m3.metric("Entities", f"{len(df_entities):,}")

    if page == "Executive Overview":
        render_overview(df_posts)
    elif page == "Content Performance":
        render_content_performance(df_posts)
    elif page == "Funnel và Conversion":
        render_funnel_conversion(df_posts)
    elif page == "Audience và Timing":
        render_audience_timing(df_posts)
    elif page == "Topic, Sentiment và Entity":
        render_topic_sentiment_entity(df_posts, df_entities)
    elif page == "Campaign Benchmark":
        render_campaign_roi(df_posts)
    elif page == "Comment Health":
        render_comment_health(df_posts, df_comments)
    else:
        render_data_quality(df_posts, df_comments)


if __name__ == "__main__":
    main()
