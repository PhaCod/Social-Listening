import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame):
    section_title(
        "Audience và Timing",
        "Tìm thời điểm đăng bài để đạt hiệu suất cao nhất.",
    )
    info_block(
        "Mục tiêu DA Marketing",
        "Dùng heatmap để chốt lịch đăng theo tuần thay vì đăng theo cảm tính.",
    )

    data = df_posts.copy()
    data["hour"] = data["timestamp"].dt.hour
    data["weekday"] = data["timestamp"].dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    heat = (
        data.groupby(["hour", "weekday"], as_index=False)
        .agg(
            avg_interaction=("interaction_score", "mean"),
            avg_discussion=("discussion_rate", "mean"),
            avg_virality=("virality_rate", "mean"),
        )
    )
    heat["weekday"] = pd.Categorical(heat["weekday"], categories=order, ordered=True)
    heat = heat.sort_values(["weekday", "hour"])

    metric = st.radio("Metric heatmap", ["avg_interaction", "avg_discussion", "avg_virality"], horizontal=True)
    fig_heat = px.density_heatmap(
        heat,
        x="weekday",
        y="hour",
        z=metric,
        histfunc="avg",
        color_continuous_scale="YlGnBu",
        title="Khung giờ vàng theo hiệu suất",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    best_slot = heat.sort_values(metric, ascending=False).head(10)
    st.markdown("### Top 10 khung giờ đề xuất")
    st.dataframe(best_slot, use_container_width=True)

    actions = []
    if not best_slot.empty:
        top_3 = best_slot.head(3)
        pretty = [f"{row['weekday']} - {int(row['hour']):02d}:00" for _, row in top_3.iterrows()]
        actions.append("Ưu tiên lịch đăng cố định tại 3 khung giờ: " + ", ".join(pretty) + ".")
    actions.append("A/B test 2 định dạng nội dung ở cùng khung giờ để biết do timing hay do creative.")
    strategy_block("Hành động lịch đăng", actions, tone="good")
