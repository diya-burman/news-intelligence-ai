import json
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Multi-Source News Intelligence", layout="wide")

# ------------------ Load Data ------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

articles = load_json("data/analyzed_articles.json")
report = load_json("data/final_report.json")

st.title("📰 Multi-Source News Intelligence Dashboard")

# ------------------ Sidebar Filters ------------------
st.sidebar.header("Filters")

sources = sorted(list(set([a.get("source") for a in articles])))
selected_sources = st.sidebar.multiselect(
    "Select Sources", sources, default=sources
)

sentiments = ["positive", "neutral", "negative"]
selected_sentiments = st.sidebar.multiselect(
    "Select Sentiment", sentiments, default=sentiments
)

filtered_articles = []
for a in articles:
    analysis = a.get("analysis", {})
    if a.get("source") in selected_sources and analysis.get("sentiment") in selected_sentiments:
        filtered_articles.append(a)

st.sidebar.markdown(f"**Showing {len(filtered_articles)} articles**")

# ------------------ Executive Summary ------------------
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📌 Executive Summary")
    st.markdown(report.get("executive_summary", "No summary available."))

with col2:
    st.subheader("📊 Quick Stats")
    st.metric("Total Articles", len(articles))
    st.metric("Filtered Articles", len(filtered_articles))

# ------------------ Bias Analysis ------------------
st.divider()
st.subheader("📊 Bias Comparison Across Sources")

bias_matrix = report.get("bias_comparison_matrix", [])
if bias_matrix:
    df_bias = pd.DataFrame(bias_matrix)
    st.dataframe(df_bias, use_container_width=True)

bias_scores = []
for a in articles:
    bs = a.get("analysis", {}).get("bias_score")
    if bs is not None:
        bias_scores.append({
            "Source": a.get("source"),
            "Bias Score": bs
        })

if bias_scores:
    df_scores = pd.DataFrame(bias_scores)
    fig = px.box(df_scores, x="Source", y="Bias Score")
    st.plotly_chart(fig, use_container_width=True)

# ------------------ Chronology ------------------
st.divider()
st.subheader("🕒 Chronological Key Facts")

facts = report.get("key_facts_chronology", [])
if facts:
    for f in facts:
        st.markdown(f"**📅 {f.get('date','Unknown')}**")
        st.markdown(f"- {f.get('fact','')}")
        st.caption("Sources: " + ", ".join(f.get("sources_supporting", [])))
else:
    st.info("No chronological facts available.")

# ------------------ Contradictions ------------------
st.divider()
st.subheader("⚠️ Conflicting Coverage")

conflicts = report.get("contradictions_or_conflicts", [])
if conflicts:
    for c in conflicts:
        with st.expander(c.get("issue", "Conflict")):
            claims = c.get("source_claims", {})
            for src, claim in claims.items():
                st.markdown(f"**{src}:** {claim}")
            st.caption("Likely reason: " + c.get("likely_reason", "unclear"))
else:
    st.success("No major contradictions detected.")

# ------------------ Articles Section ------------------
st.divider()
st.subheader("🗂️ Article Analysis")

for a in filtered_articles:
    analysis = a.get("analysis", {})

    with st.container():
        st.markdown(f"### {a.get('headline','(No headline)')}")
        st.caption(f"{a.get('source')} | {a.get('publication_date')}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Sentiment", analysis.get("sentiment"))
        c2.metric("Bias Score", analysis.get("bias_score"))
        c3.write("**Tags:**")
        c3.write(", ".join(analysis.get("topic_tags", [])))

        st.markdown("**Summary**")

        summary = analysis.get("summary")
        if isinstance(summary, list):
            for point in summary:
                st.markdown(f"- {point}")
        elif isinstance(summary, str):
            st.write(summary)
        else:
            st.write("Summary unavailable.")

        if a.get("url"):
            st.markdown(f"[🔗 Open Article]({a['url']})")

        st.divider()

# ------------------ Actionable Insights ------------------
st.divider()
st.subheader("✅ Actionable Insights")

insights = report.get("actionable_insights", [])
if insights:
    for i in insights:
        st.markdown(f"👉 **{i}**")
else:
    st.info("No actionable insights available.")
    