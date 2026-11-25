import streamlit as st
import uuid

from langgraph.types import Command
from app.graph.first_graph import graph


st.set_page_config(
    page_title="CreatorMesh | AI Content Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- THEME -------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    :root {
        --cm-bg: #090b13;
        --cm-panel: rgba(19, 23, 39, .78);
        --cm-line: rgba(157, 165, 205, .14);
        --cm-violet: #9b8cff;
        --cm-cyan: #67e8dc;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 4% 3%, rgba(112, 87, 237, .22), transparent 28%),
            radial-gradient(ellipse at 94% 12%, rgba(29, 190, 190, .13), transparent 26%),
            linear-gradient(180deg, #0b0d17 0%, #090b13 58%, #0d1020 100%);
        color: #f5f6ff;
    }
    .block-container {
        max-width: 1380px;
        padding-top: 1.3rem;
        padding-bottom: 4rem;
    }
    header[data-testid="stHeader"] { background: rgba(9,11,19,.55); }
    [data-testid="stToolbar"] { right: 1rem; }
    h1, h2, h3 { letter-spacing: -.035em; }
    h2 { font-weight: 800 !important; }
    h3 { font-weight: 750 !important; }
    [data-testid="stSidebar"] {
        background: rgba(19, 22, 35, .96);
        border-right: 1px solid rgba(255,255,255,.08);
    }
    .brand-mark {
        width: 48px; height: 48px; border-radius: 15px;
        display: flex; align-items: center; justify-content: center;
        font-size: 25px;
        background: linear-gradient(135deg, #7657f6, #12b8b0);
        box-shadow: 0 8px 24px rgba(103, 82, 235, .28);
    }
    .eyebrow {
        color: #9b91f7; font-size: .76rem; font-weight: 800;
        letter-spacing: .15em; text-transform: uppercase;
    }
    .hero-shell {
        position: relative; overflow: hidden;
        border: 1px solid rgba(166, 154, 255, .19);
        background: linear-gradient(115deg, rgba(31, 29, 61, .94), rgba(14, 31, 48, .86));
        border-radius: 26px; padding: clamp(1.5rem, 4vw, 3.2rem);
        box-shadow: 0 24px 80px rgba(0,0,0,.22);
        margin: .8rem 0 2rem 0;
    }
    .hero-shell:after {
        content: ""; position: absolute; width: 330px; height: 330px;
        right: -100px; top: -170px; border-radius: 50%;
        background: radial-gradient(circle, rgba(103,232,220,.22), transparent 68%);
        pointer-events: none;
    }
    .hero-title {
        font-size: clamp(2.25rem, 5vw, 4rem);
        font-weight: 800; letter-spacing: -.065em; line-height: 1.02;
        margin: .55rem 0 .8rem 0; max-width: 780px;
    }
    .hero-subtitle { color: #b6bdd0; font-size: 1.02rem; max-width: 680px; line-height: 1.65; }
    .hero-chip {
        display: inline-flex; align-items: center; gap: 8px;
        border: 1px solid rgba(151,139,255,.28);
        background: rgba(123,103,255,.12); color: #c8c0ff;
        border-radius: 999px; padding: 7px 12px;
        font-size: .73rem; font-weight: 800; letter-spacing: .1em;
        text-transform: uppercase;
    }
    .section-kicker {
        color: #9c91ff; font-size: .72rem; font-weight: 800;
        letter-spacing: .14em; text-transform: uppercase;
        margin-bottom: .25rem;
    }
    .panel {
        border: 1px solid var(--cm-line);
        background: var(--cm-panel);
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--cm-line) !important;
        background: rgba(17, 21, 36, .68);
        border-radius: 20px !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid var(--cm-line);
        border-radius: 14px;
        background: rgba(18,22,37,.55);
    }
    .panel-label {
        color: #a9a4d8; font-size: .74rem; font-weight: 800;
        letter-spacing: .11em; text-transform: uppercase;
        margin-bottom: .45rem;
    }
    .metric-card {
        border: 1px solid var(--cm-line);
        background: linear-gradient(145deg, rgba(31,36,59,.9), rgba(15,19,32,.94));
        border-radius: 17px; padding: 1.05rem 1.15rem;
        min-height: 116px;
        box-shadow: 0 12px 35px rgba(0,0,0,.12);
        transition: transform .2s ease, border-color .2s ease;
    }
    .metric-card:hover { transform: translateY(-3px); border-color: rgba(155,140,255,.38); }
    .metric-label { color: #a7adbd; font-size: .82rem; }
    .metric-value { font-size: 1.8rem; font-weight: 800; margin-top: .2rem; }
    .post-preview {
        white-space: pre-wrap; overflow-wrap: anywhere;
        background: linear-gradient(145deg, rgba(14,18,32,.98), rgba(18,22,40,.96));
        border: 1px solid rgba(139, 126, 245, .27);
        border-radius: 18px; padding: 1.5rem;
        line-height: 1.85; font-size: 1rem;
        box-shadow: 0 18px 45px rgba(0,0,0,.16);
    }
    .preview-topline {
        display:flex; justify-content:space-between; align-items:center;
        gap:12px; margin-bottom:12px; color:#9da6bf; font-size:.76rem;
        letter-spacing:.09em; font-weight:800; text-transform:uppercase;
    }
    .live-dot {
        display:inline-block; width:7px; height:7px; border-radius:50%;
        background:#67e8a5; box-shadow:0 0 12px rgba(103,232,165,.8);
        margin-right:7px;
    }
    .muted { color: #a7adbd; }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(105deg, #765cf5 0%, #4b8ef4 55%, #20b8b1 100%);
        border: 0; color: white; font-weight: 800;
        border-radius: 12px; min-height: 2.9rem;
        box-shadow: 0 9px 25px rgba(99,83,230,.23);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 13px 30px rgba(99,83,230,.34);
    }
    div.stButton > button {
        border-radius: 11px; min-height: 2.7rem;
        border-color: rgba(160,170,200,.22);
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
        background: rgba(10,13,24,.72) !important;
        border-color: rgba(160,170,200,.2) !important;
        border-radius: 11px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 7px; background: rgba(17,21,36,.72);
        border: 1px solid var(--cm-line); border-radius: 13px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9px; padding: 9px 15px; height: auto;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(121,103,245,.2);
    }
    div[data-testid="stAlert"] { border-radius: 13px; }
    @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .hero-shell { border-radius: 20px; }
        .metric-card { min-height: 95px; }
    }
    div[data-testid="stMetric"] {
        background: transparent;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- HELPERS -------------------------


def reset_form():
    st.session_state["topic_input"] = ""
    st.session_state["audience_input"] = ""
    st.session_state["platform_input"] = "LinkedIn"
    st.session_state.pop("workflow_result", None)
    st.session_state.pop("workflow_config", None)
    st.session_state.pop("human_review_feedback", None)


def metric_card(label, value, icon):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{icon} &nbsp; {label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_claim(claim, index):
    with st.container(border=True):
        st.markdown(f"**Claim {index}:** {claim.get('claim', '')}")
        claim_status = claim.get("status", "unknown").lower()

        if claim_status == "supported":
            st.success("✓ Supported")
        elif claim_status == "uncertain":
            st.warning("⚠ Uncertain")
        elif claim_status == "unsupported":
            st.error("✕ Unsupported")
        else:
            st.info(f"Status: {claim_status}")

        st.markdown("**Evidence**")
        st.write(claim.get("evidence") or "No evidence available.")

        urls = claim.get("source_urls", [])
        st.markdown("**Sources**")
        if urls:
            for url in urls:
                st.markdown(f"- [{url}]({url})")
        else:
            st.caption("No sources available.")


# ------------------------- SIDEBAR -------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px;margin:8px 0 22px 0;">
            <div class="brand-mark">🤖</div>
            <div>
                <div style="font-size:1.25rem;font-weight:800;">CreatorMesh</div>
                <div style="font-size:.75rem;color:#9da5b8;">AI CONTENT STUDIO</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Your workspace")
    st.caption("Create, verify and refine platform-ready content with specialized AI agents.")
    st.divider()
    st.markdown("**Workflow pipeline**")
    st.markdown(
        """
        <div style="line-height:2.15;color:#c4c9d7;">
        🧭 &nbsp; Planner<br>
        🔎 &nbsp; Researcher<br>
        ✍️ &nbsp; Writer<br>
        🛡️ &nbsp; Fact Checker<br>
        ✨ &nbsp; Editor<br>
        👤 &nbsp; Human Review
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("CreatorMesh · Multi-Agent AI Pipeline")


# ------------------------- HEADER -------------------------

st.markdown(
    '''
    <div class="hero-shell">
        <div class="hero-chip"><span class="live-dot"></span> AI-powered content workspace</div>
        <div class="hero-title">Your ideas.<br><span style="background:linear-gradient(90deg,#b2a6ff,#73e7dc);-webkit-background-clip:text;background-clip:text;color:transparent;">Amplified by AI.</span></div>
        <div class="hero-subtitle">A creative command center where specialist agents research, write, fact-check and polish your next great social post.</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# ------------------------- INPUT PANEL -------------------------

st.markdown('<div class="section-kicker">01 / Start creating</div>', unsafe_allow_html=True)
st.markdown("### Shape your next post")
st.markdown('<div class="muted">Set the direction. Your AI team will take it from there.</div>', unsafe_allow_html=True)
st.write("")

with st.container(border=True):
    input_col1, input_col2 = st.columns([1.25, 1])

    with input_col1:
        topic = st.text_input(
            "What should we write about?",
            placeholder="e.g. How AI is transforming education",
            key="topic_input",
        )
        target_audience = st.text_input(
            "Who is this for?",
            placeholder="e.g. Teachers, educators and students",
            key="audience_input",
        )

    with input_col2:
        platform = st.selectbox(
            "Choose your platform",
            ["LinkedIn", "Instagram", "X (Twitter)"],
            key="platform_input",
        )
        st.markdown(
            """
            <div class="panel" style="margin-top:8px;">
                <div class="panel-label">Your AI team</div>
                <div style="font-weight:700;">6 specialist stages</div>
                <div class="muted" style="font-size:.86rem;margin-top:4px;">
                    From topic planning to editorial approval and human review.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    action_col, reset_col, _ = st.columns([1.5, 1, 2])

    with action_col:
        generate = st.button("🚀  Generate content", type="primary", use_container_width=True)
    with reset_col:
        st.button("↻  Start fresh", on_click=reset_form, use_container_width=True)


# ------------------------- GENERATE WORKFLOW -------------------------

if generate:
    if topic.strip() and target_audience.strip():
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}

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

        try:
            with st.status("CreatorMesh agents are working...", expanded=True) as progress:
                result = graph.invoke(initial_state, config=config)
                progress.update(
                    label="Workflow execution completed!",
                    state="complete",
                    expanded=False,
                )

            st.session_state["workflow_config"] = config
            st.session_state["workflow_result"] = result
            st.rerun()
        except Exception as e:
            st.error(f"Workflow failed: {e}")
    else:
        st.warning("Please enter both a topic and target audience.")

# ------------------------- RESULTS -------------------------

if "workflow_result" in st.session_state:
    result = st.session_state["workflow_result"]
    draft = result.get("draft", "")
    status = result.get("status", "UNKNOWN")
    activity = result.get("agent_activity", [])
    fact_results = result.get("fact_check_results", [])
    interrupted = bool(result.get("__interrupt__"))

    st.divider()
    st.markdown('<div class="section-kicker">02 / Live workspace</div>', unsafe_allow_html=True)
    st.markdown("## Your content overview")

    if status == "EDITOR_APPROVED":
        st.success("✓ Content approved by Editor")
    elif status == "HUMAN_APPROVED":
        st.success("✓ Content approved by Human Reviewer")
    elif interrupted:
        st.warning("⏸ Human review needed — your feedback is required to continue.")
    elif status == "FACT_CHECK_REVISION_REQUIRED":
        st.warning("⚠ Fact-check revision required")
    else:
        st.info(f"Workflow status: {status}")

    total_revisions = (
        result.get("revision_count", 0)
        + result.get("fact_revision_count", 0)
        + result.get("human_revision_count", 0)
    )
    total_claims = sum(len(run.get("checks", [])) for run in fact_results)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Agent activities", len(activity), "🤖")
    with m2:
        metric_card("Total revisions", total_revisions, "🔁")
    with m3:
        metric_card("Fact-check runs", len(fact_results), "🛡️")
    with m4:
        metric_card("Claims checked", total_claims, "📑")

    st.write("")
    content_tab, fact_tab, activity_tab = st.tabs(
        ["✍️  Generated content", "🛡️  Fact checker", "🤖  Agent activity"]
    )

    with content_tab:
        st.markdown("### Your content")
        if draft:
            st.markdown(
                '<div class="preview-topline"><span>Post preview</span><span><span class="live-dot"></span>Ready to review</span></div>',
                unsafe_allow_html=True,
            )
            # Native Streamlit code block provides a built-in Copy button.
            st.code(draft, language=None, wrap_lines=True)
            selected_platform = result.get("platform", platform)
            safe_platform = (
                selected_platform.lower()
                .replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
            )
            st.write("")
            st.download_button(
                "📥  Download post",
                data=draft,
                file_name=f"creatormesh_{safe_platform}_post.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.caption("Tip: Hover over the post preview and use the Copy button in the top-right corner.")
        else:
            st.info("No generated content available yet.")

    with fact_tab:
        st.markdown("### Verification report")
        if fact_results:
            for run_index, run in enumerate(fact_results, start=1):
                checks = run.get("checks", [])
                with st.expander(f"Fact Check Run {run_index} · {len(checks)} claims", expanded=(run_index == len(fact_results))):
                    if not checks:
                        st.info("No factual claims identified in this run.")
                    for claim_index, claim in enumerate(checks, start=1):
                        show_claim(claim, claim_index)
        else:
            st.info("Fact-check results will appear here after the workflow runs.")

    with activity_tab:
        st.markdown("### Agent execution history")
        if activity:
            for index, item in enumerate(activity, start=1):
                agent = item.get("agent", "Agent")
                agent_status = item.get("status", "Unknown")
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    with left:
                        st.markdown(f"**{index:02d} · {agent}**")
                    with right:
                        if agent_status == "Approved":
                            st.success(agent_status)
                        elif agent_status == "Rejected":
                            st.error(agent_status)
                        else:
                            st.info(agent_status)
        else:
            st.info("Agent activity will appear here.")

    # ------------------------- HUMAN REVIEW -------------------------

    if interrupted:
        st.divider()
        st.markdown("## 👤 Human review")
        st.markdown(
            "Review the draft above. Share specific changes, or type **approve** to approve it."
        )
        feedback = st.text_area(
            "Your feedback",
            placeholder="Example: Remove unsupported claims, make the opening stronger, and keep the post concise...",
            key="human_review_feedback",
            height=120,
        )

        if st.button("Submit review and continue", type="primary", use_container_width=True):
            if feedback.strip():
                try:
                    with st.spinner("Resuming CreatorMesh workflow..."):
                        updated_result = graph.invoke(
                            Command(resume=feedback.strip()),
                            config=st.session_state["workflow_config"],
                        )
                    st.session_state["workflow_result"] = updated_result
                    st.rerun()
                except Exception as e:
                    st.error(f"Review submission failed: {e}")
            else:
                st.warning("Please enter feedback or approve.")

st.divider()
st.markdown(
    '<div style="text-align:center;color:#858da2;font-size:.82rem;">CreatorMesh · Built for thoughtful, evidence-aware social content</div>',
    unsafe_allow_html=True,
)
