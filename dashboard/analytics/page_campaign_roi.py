import pandas as pd
import plotly.express as px
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame):
    section_title(
        "Campaign Benchmark",
        "So sánh campaign theo hiệu suất tương tác thực tế có thể lấy từ Facebook.",
    )
    info_block(
        "Nguyên tắc ra quyết định",
        "Interaction cao + share rate tốt => Scale. Interaction thấp + sentiment xấu => cần tối ưu thông điệp.",
    )

    by_campaign = (
        df_posts.groupby(["campaign_type", "content_pillar"], as_index=False)
        .agg(
            posts=("post_id", "count"),
            likes=("likes", "sum"),
            comments=("total_comments", "sum"),
            shares=("total_shares", "sum"),
            interaction=("interaction_score", "sum"),
            avg_virality=("virality_rate", "mean"),
            negative_rate=("sentiment", lambda s: (s == "Tiêu cực").mean()),
        )
    )
    by_campaign["interaction_per_post"] = by_campaign["interaction"] / by_campaign["posts"].clip(lower=1)
    by_campaign["share_rate"] = by_campaign["shares"] / by_campaign["interaction"].clip(lower=1)

    fig_perf = px.bar(
        by_campaign,
        x="campaign_type",
        y="interaction_per_post",
        color="content_pillar",
        title="Interaction/Post theo campaign và pillar",
    )
    st.plotly_chart(fig_perf, use_container_width=True)

    fig_quality = px.scatter(
        by_campaign,
        x="share_rate",
        y="negative_rate",
        color="campaign_type",
        size="interaction_per_post",
        hover_data=["content_pillar", "interaction_per_post"],
        title="Bản đồ chất lượng campaign: Share rate vs Negative rate",
    )
    st.plotly_chart(fig_quality, use_container_width=True)

    st.dataframe(by_campaign.sort_values("interaction_per_post", ascending=False), use_container_width=True)

    grouped = by_campaign.groupby("campaign_type", as_index=False).agg(
        interaction_per_post=("interaction_per_post", "mean"),
        negative_rate=("negative_rate", "mean"),
    )
    to_scale = grouped.sort_values(["interaction_per_post", "negative_rate"], ascending=[False, True]).head(1)
    to_fix = grouped.sort_values(["interaction_per_post", "negative_rate"], ascending=[True, False]).head(1)

    actions = []
    if not to_scale.empty:
        actions.append(f"Scale ngân sách cho {to_scale.iloc[0]['campaign_type']} trong 7 ngày tới.")
    if not to_fix.empty:
        actions.append(f"Tối ưu nội dung cho {to_fix.iloc[0]['campaign_type']} do interaction thấp và sentiment rủi ro.")
    actions.append("Giữ rule đánh giá campaign theo chu kỳ 3 ngày dựa trên interaction và sentiment.")
    strategy_block("Hành động ngân sách", actions, tone="warn")
