import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics.ui import info_block, section_title, strategy_block


def render(df_posts: pd.DataFrame):
    section_title(
        "Funnel và Conversion",
        "Theo dõi rơi rụng từ nhìn thấy bài viết đến đặt hàng.",
    )
    info_block(
        "Mục tiêu DA Marketing",
        "Xác định tầng rơi rụng lớn nhất từ đăng bài -> có tương tác -> có bình luận -> có chia sẻ để tối ưu đúng điểm nghẽn.",
    )

    interacted_posts = int((df_posts["interaction_score"] > 0).sum())
    discussed_posts = int((df_posts["total_comments"] > 0).sum())
    shared_posts = int((df_posts["total_shares"] > 0).sum())

    totals = {
        "Posts": int(len(df_posts)),
        "Interacted Posts": interacted_posts,
        "Commented Posts": discussed_posts,
        "Shared Posts": shared_posts,
    }

    fig_funnel = go.Figure(
        go.Funnel(
            y=list(totals.keys()),
            x=list(totals.values()),
            textinfo="value+percent previous",
            marker={"color": ["#386641", "#6a994e", "#a7c957", "#f2e8cf"]},
        )
    )
    fig_funnel.update_layout(title="Marketing funnel - Thánh Riviu")
    st.plotly_chart(fig_funnel, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    interaction_penetration = totals["Interacted Posts"] / max(totals["Posts"], 1)
    discussion_penetration = totals["Commented Posts"] / max(totals["Interacted Posts"], 1)
    share_penetration = totals["Shared Posts"] / max(totals["Commented Posts"], 1)
    c1.metric("Interaction penetration", f"{interaction_penetration:.2%}")
    c2.metric("Discussion penetration", f"{discussion_penetration:.2%}")
    c3.metric("Share penetration", f"{share_penetration:.2%}")

    by_campaign = (
        df_posts.groupby("campaign_type", as_index=False)
        .agg(
            posts=("post_id", "count"),
            likes=("likes", "sum"),
            comments=("total_comments", "sum"),
            shares=("total_shares", "sum"),
            interaction=("interaction_score", "sum"),
        )
    )
    by_campaign["discussion_rate"] = by_campaign["comments"] / (by_campaign["interaction"].clip(lower=1))
    by_campaign["share_rate"] = by_campaign["shares"] / (by_campaign["interaction"].clip(lower=1))

    fig = px.bar(
        by_campaign,
        x="campaign_type",
        y="interaction",
        color="share_rate",
        text_auto=True,
        title="Interaction và Share Rate theo campaign",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(by_campaign.sort_values("interaction", ascending=False), use_container_width=True)

    interaction_to_discussion = totals["Commented Posts"] / max(totals["Interacted Posts"], 1)
    discussion_to_share = totals["Shared Posts"] / max(totals["Commented Posts"], 1)

    actions = []
    if interaction_to_discussion < 0.4:
        actions.append("Bài đã có tương tác nhưng ít bình luận: thêm câu hỏi chốt cuối bài để kéo thảo luận.")
    if discussion_to_share < 0.3:
        actions.append("Bình luận có nhưng share thấp: tăng format 'mẹo hữu ích' và CTA chia sẻ rõ ràng.")
    if not actions:
        actions.append("Funnel tương tác ổn: duy trì nhịp nội dung và scale campaign có share_rate cao nhất.")

    strategy_block("Hành động funnel", actions, tone="warn" if len(actions) > 1 else "good")
