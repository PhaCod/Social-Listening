import numpy as np
import pandas as pd
import streamlit as st

from analytics.constants import CAMPAIGNS, CONTENT_PILLARS, ENTITY_POOLS, POST_TYPES, SENTIMENTS, TOPICS


@st.cache_data
def build_mock_data(seed: int = 20260323, n_posts: int = 240) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2026-01-15")

    post_rows = []
    comment_rows = []

    for idx in range(n_posts):
        ts = start + pd.to_timedelta(int(rng.integers(0, 70 * 24)), unit="h")
        topic = rng.choice(TOPICS, p=[0.16, 0.34, 0.14, 0.13, 0.23])
        sentiment = rng.choice(SENTIMENTS, p=[0.53, 0.3, 0.17])
        post_type = rng.choice(POST_TYPES, p=[0.42, 0.18, 0.17, 0.17, 0.06])
        pillar = rng.choice(CONTENT_PILLARS, p=[0.28, 0.2, 0.19, 0.16, 0.17])
        campaign = rng.choice(CAMPAIGNS, p=[0.44, 0.28, 0.17, 0.11])

        likes = int(rng.integers(15, 3400))
        total_comments = int(rng.integers(0, 260))
        total_shares = int(rng.integers(0, 180))

        interaction_score = likes + (2 * total_comments) + (3 * total_shares)
        discussion_rate = total_comments / max(likes + total_comments + total_shares, 1)
        virality_rate = total_shares / max(likes + total_comments + total_shares, 1)

        entities = {
            "restaurants": list(rng.choice(ENTITY_POOLS["restaurants"], size=int(rng.integers(0, 3)), replace=False)),
            "dishes": list(rng.choice(ENTITY_POOLS["dishes"], size=int(rng.integers(0, 3)), replace=False)),
            "locations": list(rng.choice(ENTITY_POOLS["locations"], size=int(rng.integers(0, 2)), replace=False)),
        }

        source_url = f"https://facebook.com/thanh-riviu/posts/{300000 + idx}"
        content_length = int(rng.integers(40, 720))
        content = f"Post {idx + 1} | {pillar} | {topic} | {post_type}"

        # Simulate parser/data quality issues.
        is_suspected_post_comment_mix = bool(rng.random() < 0.08)
        if is_suspected_post_comment_mix:
            content = f"Reply: {content}"
        if rng.random() < 0.05:
            sentiment = None
        if rng.random() < 0.06:
            topic = None
        if rng.random() < 0.04:
            source_url = "N/A"

        post_id = f"facebook_{idx:06d}"
        post_rows.append(
            {
                "post_id": post_id,
                "platform": "facebook",
                "source_url": source_url,
                "author": "Thánh Riviu",
                "content": content,
                "content_length": content_length,
                "timestamp": ts,
                "post_type": post_type,
                "content_pillar": pillar,
                "campaign_type": campaign,
                "topic": topic,
                "sentiment": sentiment,
                "likes": likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "interaction_score": interaction_score,
                "discussion_rate": discussion_rate,
                "virality_rate": virality_rate,
                "is_suspected_post_comment_mix": is_suspected_post_comment_mix,
                "entities": entities,
            }
        )

        for c_idx in range(total_comments):
            c_sent = rng.choice(SENTIMENTS, p=[0.48, 0.33, 0.19]) if rng.random() > 0.08 else None
            c_react = int(rng.integers(0, 160))
            c_content = f"Comment {c_idx + 1} on {post_id}"
            if rng.random() < 0.045:
                c_content = f"See Translation {c_content}"

            comment_rows.append(
                {
                    "post_id": post_id,
                    "author": f"commenter_{int(rng.integers(1, 850)):03d}",
                    "content": c_content,
                    "sentiment": c_sent,
                    "reactions": c_react,
                    "is_noise_ui_text": c_content.startswith("See Translation"),
                }
            )

    df_posts = pd.DataFrame(post_rows)
    df_comments = pd.DataFrame(comment_rows)

    entity_rows = []
    for _, row in df_posts.iterrows():
        for key in ["restaurants", "dishes", "locations"]:
            for item in row["entities"][key]:
                entity_rows.append(
                    {
                        "post_id": row["post_id"],
                        "entity_type": key,
                        "entity_value": item,
                        "interaction_score": row["interaction_score"],
                        "post_sentiment": row["sentiment"],
                        "virality_rate": row["virality_rate"],
                    }
                )

    df_entities = pd.DataFrame(entity_rows)
    return df_posts, df_comments, df_entities
