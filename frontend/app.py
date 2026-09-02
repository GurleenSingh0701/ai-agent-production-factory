import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_URL", "https://ai-agent-factory.onrender.com")

st.set_page_config(page_title="AI Agent Factory", page_icon="🤖", layout="centered")

st.title("🤖 AI Agent Production Factory")
st.markdown("Deploying production-ready agents every day for 30 days.")

AGENTS = {
    "Lead Qualification Agent": "lead_gen",
    "Email Triage Agent": "email_triage",
    "Meeting Minutes Agent": "meeting_minutes",
}

selected_agent_name = st.selectbox("Select an Agent", options=list(AGENTS.keys()))
agent_id = AGENTS[selected_agent_name]

st.divider()
user_input = {}

if agent_id == "email_triage":
    st.subheader("📧 Email Triage & Draft Agent")
    sender = st.text_input("Sender Name")
    body = st.text_area("Email Body")
    user_input = {"sender_name": sender, "email_body": body}

elif agent_id == "lead_gen":
    st.subheader("🎯 Lead Qualification Agent")
    url = st.text_input("Company URL")
    icp = st.text_area("Ideal Customer Profile (ICP)")
    user_input = {"url": url, "icp": icp}

elif agent_id == "meeting_minutes":
    st.subheader("📝 Meeting Minutes $\rightarrow$ Action Items")
    transcript = st.text_area("Meeting Transcript", height=300)
    user_input = {"transcript": transcript}

if st.button("Run Agent", type="primary"):
    if not user_input or not all(str(val).strip() for val in user_input.values()):
        st.error("Please fill in all required fields.")
    else:
        with st.spinner(f"Running {selected_agent_name}..."):
            try:
                response = requests.post(f"{API_BASE_URL}/run/{agent_id}", json={"input": user_input}, timeout=120)
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get("status") == "success":
                        result = res_json.get("data", {})
                        st.success("Agent Execution Complete!")

                        if "fit_score" in result: # Day 1
                            st.metric("Fit Score", f"{result['fit_score']}/100")
                            st.write(f"**Reasoning:** {result.get('reasoning', '')}")
                        elif "draft_response" in result: # Day 2
                            st.markdown("### 📝 Draft Response")
                            st.write(result.get("draft_response", ""))
                        elif "summary" in result: # Day 3
                            st.markdown("### 📌 Summary")
                            st.write(result.get("summary"))
                            st.markdown("### ✅ Action Items")
                            for item in result.get("action_items", []):
                                st.success(f"**{item['assignee']}**: {item['task']} (📅 {item['deadline'] or 'N/A'})")
                            st.markdown("### ⚖️ Key Decisions")
                            for dec in result.get("key_decisions", []):
                                st.info(dec)
                    else:
                        st.error(res_json.get("data", {}).get("error", "Unknown error"))
                else:
                    st.error(f"Error {response.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
