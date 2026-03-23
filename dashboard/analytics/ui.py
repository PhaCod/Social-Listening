import streamlit as st


def section_title(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def info_block(title: str, body: str):
    st.markdown(
        f"""
        <div style="padding:12px 14px;border:1px solid rgba(148,163,184,.25);border-radius:12px;
                    background:linear-gradient(180deg, rgba(15,23,42,.42), rgba(2,6,23,.30));margin:8px 0 12px 0;">
            <div style="font-weight:700;margin-bottom:6px;">{title}</div>
            <div style="font-size:0.96rem;line-height:1.45;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def strategy_block(title: str, actions: list[str], tone: str = "info"):
    if not actions:
        return

    icon = "🎯"
    if tone == "good":
        icon = "✅"
    elif tone == "warn":
        icon = "⚠️"

    text = "\n".join([f"- {a}" for a in actions])
    st.markdown(f"### {icon} {title}")
    st.markdown(text)
