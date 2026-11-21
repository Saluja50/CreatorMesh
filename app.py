
import streamlit as st

st.set_page_config(
    page_title="CreatorMesh",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 CreatorMesh")
st.subheader("AI-Powered Social Media Content Pipeline")

topic = st.text_input(
    "Enter your content topic",
    placeholder="e.g. Future of Artificial Intelligence",
)

platform = st.selectbox(
    "Select platform",
    ["LinkedIn"],
)

target_audience = st.text_input(
    "Target audience",
    placeholder="e.g. Software developers",
)

if st.button("Generate Content"):
    if topic.strip() and target_audience.strip():
        st.success("Input received! Backend integration is our next step.")
        st.write("**Topic:**", topic)
        st.write("**Platform:**", platform)
        st.write("**Audience:**", target_audience)
    else:
        st.warning("Please enter both topic and target audience.")
