import streamlit as st
import requests
import os 

API_BASE_URL = os.getenv("API_URL", "https://ai-agent-factory-api.onrender.com")


st.set_page_config(page_title="AI Agent Factory", page_icon="🤖")

st.title("🤖 AI Agent Production Factory")
st.markdown("Deploying production-ready agents every day for 30 days.")

# 1. Agent Selection
# You can add your new agents to this list every day
agents = {
    "Lead Qualification Agent": "lead_gen",
    # "Email Triage Agent": "email_triage", <-- Add tomorrow
}

selected_agent_name = st.selectbox("Select an Agent", options=list(agents.keys()))
agent_id = agents[selected_agent_name]

st.divider()

# 2. Dynamic Input Section
user_input = {}

if agent_id == "lead_gen":
    st.subheader("Lead Qualification")
    url = st.text_input("Company URL", placeholder="https://www.nvidia.com")
    icp = st.text_area("Ideal Customer Profile (ICP)", placeholder="Enter your target customer description...")
    user_input = {"url": url, "icp": icp}

if st.button("Run Agent"):
    if not user_input or not all(user_input.values()):
        st.error("Please provide the required inputs.")
    else:
        with st.spinner(f"Running {selected_agent_name}..."):
            try:
                # Connect to the FastAPI backend running in the other container
                response = requests.post(f"{API_BASE_URL}/run/{agent_id}", json={"input": user_input})

                
                if response.status_code == 200:
                    result = response.json()["data"]
                    
                    st.success("Agent Execution Complete!")
                    
                    # Display results beautifully
                    if "fit_score" in result:
                        st.metric("Fit Score", f"{result['fit_score']}/100")
                        st.write(f"**Reasoning:** {result['reasoning']}")
                        st.info(f"**Action:** {result['recommended_action']}")
                    else:
                        st.json(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
