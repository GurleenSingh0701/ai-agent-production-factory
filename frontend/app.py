import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_URL", "https://ai-agent-factory-api.onrender.com")

st.set_page_config(page_title="AI Agent Factory", page_icon="🤖", layout="centered")

st.title("🤖 AI Agent Production Factory")
st.markdown("Deploying production-ready agents every day for 30 days.")

# Consolidated dictionary of available agents
AGENTS = {
    "Lead Qualification Agent": "lead_gen",
    "Email Triage Agent": "email_triage",
}

selected_agent_name = st.selectbox("Select an Agent", options=list(AGENTS.keys()))
agent_id = AGENTS[selected_agent_name]

st.divider()

user_input = {}

# Dynamic Input Section
if agent_id == "email_triage":
    st.subheader("📧 Email Triage & Draft Agent")
    sender = st.text_input("Sender Name", placeholder="e.g. John Doe")
    body = st.text_area("Email Body", placeholder="Paste the email content here...")
    user_input = {"sender_name": sender, "email_body": body}

elif agent_id == "lead_gen":
    st.subheader("🎯 Lead Qualification Agent")
    url = st.text_input("Company URL", placeholder="https://www.nvidia.com")
    icp = st.text_area("Ideal Customer Profile (ICP)", placeholder="Enter your target customer description...")
    user_input = {"url": url, "icp": icp}

# Unified Run Agent Trigger
if st.button("Run Agent", type="primary"):
    if not user_input or not all(str(val).strip() for val in user_input.values()):
        st.error("Please fill in all required fields.")
    else:
        with st.spinner(f"Running {selected_agent_name}..."):
            try:
                # Send request using standard AgentRequest schema {"input": user_input}
                response = requests.post(
                    f"{API_BASE_URL}/run/{agent_id}",
                    json={"input": user_input},
                    timeout=60,
                )

                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get("status") == "success":
                        result = res_json.get("data", {})
                        st.success("Agent Execution Complete!")

                        # Render agent specific output
                        if "fit_score" in result:
                            st.metric("Fit Score", f"{result['fit_score']}/100")
                            st.write(f"**Reasoning:** {result.get('reasoning', '')}")
                            st.info(f"**Action:** {result.get('recommended_action', '')}")

                        elif "draft_response" in result:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Category", result.get("category", "N/A"))
                            with col2:
                                st.metric("Priority", result.get("priority", "N/A"))
                            with col3:
                                st.metric("Sentiment", result.get("sentiment", "N/A"))

                            st.markdown("### 📝 Draft Response")
                            st.write(result.get("draft_response", ""))
                        else:
                            st.json(result)
                    else:
                        st.error(f"Agent Execution Error: {res_json.get('data', {}).get('error', 'Unknown error')}")
                else:
                    st.error(f"HTTP Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
