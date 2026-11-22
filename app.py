
import streamlit as st
import uuid

from langgraph.types import Command
from app.graph.first_graph import graph



st.set_page_config(
    page_title="CreatorMesh",
    page_icon="🤖",
    layout="wide",
)
def reset_form():
    st.session_state["topic_input"] = ""
    st.session_state["audience_input"] = ""
    st.session_state["platform_input"] = "LinkedIn"

    st.session_state.pop("workflow_result", None)
    st.session_state.pop("workflow_config", None)


st.title("🤖 CreatorMesh")
st.subheader("AI-Powered Social Media Content Pipeline")

topic = st.text_input(
    "Enter your content topic",
    placeholder="e.g. Future of Artificial Intelligence",
    key="topic_input",
)

platform = st.selectbox(
    "Select platform",
    ["LinkedIn", "Instagram", "X (Twitter)"],
    key="platform_input",
)

target_audience = st.text_input(
    "Target audience",
    placeholder="e.g. Software developers",
    key="audience_input",
)


if st.button("Generate Content"):
    if topic.strip() and target_audience.strip():

        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4())
            }
        }

        initial_state = {
            "topic": topic,
            "platform": platform,
            "target_audience": target_audience,
            "plan": {},
            "research": {},
            "draft": "",
            "editor_feedback": [],
            "editor_approved": False,
            "revision_count": 0,
            "fact_check_results": [],
            "fact_revision_count": 0,
            "fact_check_revision_requested": False,
            "status": "STARTED",
            "human_feedback": "",
            "human_revision_count": 0,
            "agent_activity": [],
        }

        progress = st.status("CreatorMesh agents are working...", expanded=True)

        try:
            result = graph.invoke(initial_state, config=config)
            progress.update(
                label="Content generation completed!",
                state="complete",
                expanded=False,
            )
        except Exception as e:
            progress.update(
                label="Workflow failed",
                state="error",
            )
            st.error(str(e))
            st.stop()

        st.session_state["workflow_config"] = config
        st.session_state["workflow_result"] = result

    else:
        st.warning("Please enter both topic and target audience.")

st.button(
    "Start New Content",
    on_click=reset_form
)



if "workflow_result" in st.session_state:
    result = st.session_state["workflow_result"]

    # Generated Content
    st.subheader("Generated Content")
    st.write(result.get("draft", ""))

    st.download_button(
        label="📥 Download Post",
        data=result.get("draft", ""),
        file_name=f"creatormesh_{platform.lower().replace(' ', '_').replace('(', '').replace(')', '')}_post.md",
        mime="text/markdown",
    )

    st.write("Status:", result.get("status"))
    # Fact Checker Results
    st.subheader("🔍 Fact Checker Results")

    fact_results = result.get("fact_check_results", [])

    if fact_results:
        for index, check in enumerate(fact_results, start=1):
            with st.container(border=True):
                st.markdown(f"**Claim {index}**")
                st.write(check)
    else:
        st.info("No fact-check results available.")
    # Agent Activity
    st.subheader("🤖 Agent Activity")

    agent_activity = result.get("agent_activity", [])

    if agent_activity:
        for index, activity in enumerate(agent_activity, start=1):
            agent = activity.get("agent", "Agent")
            status = activity.get("status", "Unknown")

            with st.container(border=True):
                st.markdown(f"**{index}. {agent}**")

                if status == "Rejected":
                    st.warning(f"⚠️ {status}")
                elif status == "Approved":
                    st.success(f"✅ {status}")
                else:
                    st.info(f"✓ {status}")
    else:
        st.info("Agent activity not available yet.")

    # Human Approval
    if result.get("status") == "HUMAN_APPROVED":
        st.success("✅ Content approved by human!")

    elif result.get("status") == "EDITOR_APPROVED":
        st.success("✅ Content approved by Editor!")

    # Human Review
    elif result.get("__interrupt__"):
        st.subheader("Human Review")

        feedback = st.text_area(
            "Review the draft and enter feedback or approve",
            placeholder="Enter feedback or type approve...",
            key="human_review_feedback",
        )

        if st.button("Submit Review"):
            if feedback.strip():
                config = st.session_state["workflow_config"]

                with st.spinner("Resuming CreatorMesh workflow..."):
                    updated_result = graph.invoke(
                        Command(resume=feedback.strip()),
                        config=config,
                    )

                st.session_state["workflow_result"] = updated_result
                st.rerun()
            else:
                st.warning("Please enter feedback or approve.")
