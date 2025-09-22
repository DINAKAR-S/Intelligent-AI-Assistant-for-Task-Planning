# streamlit_app.py
import streamlit as st
import time
import json
from datetime import datetime
from database.database import create_tables, SessionLocal
from database.models import TaskPlan
from agents.planner_agent import planner_agent  # updated import for multi-agent planner
import threading

# Page configuration
st.set_page_config(
    page_title="AI Task Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
create_tables()

# --- CSS already included as in your previous code ---

# Custom CSS for better styling
st.markdown("""
<style>
/* --- General App Styling --- */
.stApp {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header (Top Bar) */
.css-18e3th9 {
    background-color: #0d0d0d;
    padding: 0.5rem 1rem;
    color: white;
}

/* Main header */
.main-header {
    font-size: 2.5rem;
    font-weight: 800;
    text-align: center;
    margin: 1.5rem 0 0.5rem 0;
    background: linear-gradient(90deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
}

/* Subheaders */
h2, h3, h4 {
    color: #b3cde3;
    font-weight: 700;
    text-align: center;
}

/* Description text under main header */
.css-ng1t4o p {
    text-align: center;
    color: #a0a0a0;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* --- Plan Card (for "Create Your Travel Plan" section) --- */
.plan-card {
    background-color: #1e1e1e;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgb(0 0 0 / 25%);
    margin: 1.5rem auto;
    max-width: 60%; /* Adjusted to a relative percentage */
    border-left: 6px solid #667eea;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.plan-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgb(0 0 0 / 40%);
}

/* Adjusting the heading inside the plan card */
.plan-card h2 {
    color: #b3cde3;
    font-weight: 700;
    text-align: left;
    margin-bottom: 1.5rem;
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background-color: #212121;
    padding: 1rem 1rem;
    border-radius: 0 16px 16px 0;
    box-shadow: 0 8px 24px rgb(0 0 0 / 20%);
    width: 20% !important; /* Adjusted to a relative percentage */
    min-width: 150px; /* Optional: Sets a minimum size to prevent it from getting too small */
    max-width: 300px; /* Optional: Sets a maximum size to prevent it from getting too large */
}

/* Sidebar header */
[data-testid="stSidebar"] .css-heg063 {
    font-weight: 700;
    font-size: 1rem;
    color: #b3cde3;
    margin-bottom: 0.5rem;
    padding-left: 0.5rem;
}

/* Sidebar selectbox */
.stSelectbox {
    margin-bottom: 1rem;
    padding-left: 0.5rem;
}

/* Sidebar inputs */
[data-testid="stSidebar"] .stTextInput, [data-testid="stSidebar"] .stTextArea {
    margin-bottom: 1rem;
    padding-left: 0.5rem;
}

[data-testid="stSidebar"] .stTextInput > div > input,
[data-testid="stSidebar"] .stTextArea > div > div > textarea {
    background-color: #333333 !important;
    color: #e0e0e0 !important;
    border: 1px solid #555555 !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    font-size: 0.9rem;
}

/* --- Sidebar Logo/Icon Section --- */
.sidebar-logo {
    background-color: #333333;
    border-radius: 8px;
    padding: 0.5rem;
    margin-bottom: 1.5rem;
    width: fit-content;
    display: block;
    margin-left: auto;
    margin-right: auto;
}
.sidebar-logo img {
    max-width: 40px;
    height: auto;
    display: block;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 700;
    padding: 0.7rem 2rem;
    cursor: pointer;
    font-size: 1rem;
    box-shadow: 0 6px 16px rgb(102 126 234 / 20%);
    transition: all 0.25s ease;
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-top: 2rem;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgb(102 126 234 / 30%);
}

.stButton > button:focus-visible {
    outline: 3px solid #b3c7ff;
    outline-offset: 2px;
}

/* Textarea & Inputs in main content */
.stTextArea > div > div > textarea,
.stTextInput > div > input {
    color: #e0e0e0 !important;
    background-color: #1e1e1e !important;
    border-radius: 12px !important;
    border: 2px solid #333333 !important;
    font-size: 1rem;
    line-height: 1.5;
    padding: 1rem !important;
    width: 100%;
}

/* Footer (Bottom Bar) */
.css-1lsmgbg {
    background-color: #0d0d0d;
    color: #ccc;
    padding: 0.5rem 1rem;
    text-align: center;
    position: fixed;
    bottom: 0;
    width: 100%;
    z-index: 100;
}
</style>
""", unsafe_allow_html=True)
# Initialize session state
for key, value in [('plans', []), ('current_plan', None), ('planning_in_progress', False), ('current_page', "Create New Plan")]:
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------- DATABASE FUNCTIONS ----------------- #
def load_plans_from_db():
    db = SessionLocal()
    try:
        return db.query(TaskPlan).order_by(TaskPlan.created_at.desc()).all()
    finally:
        db.close()

def save_plan_to_db(plan_data):
    db = SessionLocal()
    try:
        new_plan = TaskPlan(goal=plan_data['goal'], status='completed')
        new_plan.set_plan_steps_list(plan_data['steps'])
        new_plan.set_enriched_info_dict(plan_data['enriched_info'])
        db.add(new_plan)
        db.commit()
        return new_plan.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# ----------------- PLAN GENERATION ----------------- #
def generate_plan_async(goal):
    """Generate plan in background"""
    try:
        # Use the updated multi-agent planner
        result = planner_agent.create_plan(goal)
        plan_id = save_plan_to_db(result)
        result['id'] = plan_id
        st.session_state.current_plan = result
        st.session_state.planning_in_progress = False
        return result
    except Exception as e:
        st.session_state.planning_in_progress = False
        st.session_state.current_plan = {
            'goal': goal,
            'steps': [],
            'enriched_info': {'error': f'Plan generation failed: {str(e)}'}
        }
        return None

# ----------------- STREAMLIT PAGES ----------------- #
def main():
    st.markdown('<h1 class="main-header">🤖 AI Task Planner</h1>', unsafe_allow_html=True)
    st.markdown("### Intelligent AI Assistant for Task Planning")
    st.markdown("---")

    # Sidebar navigation & stats
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        page = st.selectbox("Choose a page", ["Create New Plan", "View Plans History"], key="page_selector")
        st.markdown("---")
        st.markdown("## 📊 Quick Stats")
        plans = load_plans_from_db()
        st.metric("Total Plans", len(plans))
        if plans:
            recent_plan = plans[0]
            st.metric("Latest Plan", recent_plan.goal[:30]+"..." if len(recent_plan.goal) > 30 else recent_plan.goal)

    # Render main page
    if page == "Create New Plan":
        create_new_plan_page()
    elif page == "View Plans History":
        view_plans_history_page()
    else:
        st.error("Please select a valid page from the sidebar.")

# ----------------- CREATE NEW PLAN ----------------- #
def create_new_plan_page():
    st.markdown("## 🎯 Create Your Travel Plan")
    
    goal = st.text_area(
        "Describe your travel goal:",
        placeholder="e.g., Plan a 3-day trip to Paris focusing on art museums and local cuisine",
        height=120,
        help="Be as specific as possible for better results",
        key="goal_input"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Center the button using a single column and CSS
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <style>
        .center-button > button {
            width: 200px;
            height: 50px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("🚀 Generate Plan", key="generate_plan_logic"):
            if not goal.strip():
                st.error("Please enter a travel goal!")
                return

            st.session_state.planning_in_progress = True
            st.session_state.current_plan = None

            with st.spinner("🤖 AI Agent is analyzing your goal..."):
                result = generate_plan_async(goal)
                st.session_state.current_plan = result
                st.success("✅ Plan generated successfully!")
                st.rerun()

    # Display current plan
    if st.session_state.get("current_plan"):
        display_plan(st.session_state.current_plan)


def display_plan(plan):
    """Display a plan in a nice format with proper HTML rendering"""
    # st.markdown("---")
    # st.markdown("## 📋 Your Generated Plan")
    
    # # Display Goal
    # st.markdown(f"### 🎯 Goal: {plan['goal']}")

    # # Deduplicate steps while preserving order
    # seen = set()
    # unique_steps = []
    # for step in plan.get('steps', []):
    #     if isinstance(step, dict):
    #         step_text = step.get('description', str(step))
    #     else:
    #         step_text = str(step)
    #     if step_text not in seen:
    #         seen.add(step_text)
    #         unique_steps.append(step_text)

    # # Display steps
    # for i, step_text in enumerate(unique_steps, 1):
    #     st.markdown(f"{i}. {step_text}")

    # # Display enriched information
    # enriched_info = plan.get('enriched_info', {})
    # if enriched_info:
    #     st.markdown("### 💡 Additional Recommendations & Insights")
    #     if enriched_info.get('recommendations'):
    #         st.markdown(f"**Recommendations:** {enriched_info['recommendations']}")
    #     if enriched_info.get('weather_considerations'):
    #         st.markdown(f"**Weather Forecast:** {enriched_info['weather_considerations']}")
    #     if enriched_info.get('budget_tips'):
    #         st.markdown(f"**Budget Tips:** {enriched_info['budget_tips']}")

    # Optional: Full raw LLM output
    if plan.get('full_result'):
        st.text(plan['full_result'])




# ----------------- VIEW HISTORY ----------------- #
# ----------------- VIEW HISTORY ----------------- #
def view_plans_history_page():
    st.markdown("## 📚 Plans History")
    plans = load_plans_from_db()
    if not plans:
        st.info("No plans found. Create your first plan!")
        return

    # Search and sort UI
    col1, col2 = st.columns([3,1])
    with col1:
        search_term = st.text_input("🔍 Search plans:", placeholder="Search by goal or content...")
    with col2:
        sort_by = st.selectbox("Sort by:", ["Newest","Oldest","Goal A-Z","Goal Z-A"])

    filtered_plans = plans
    if search_term:
        filtered_plans = [p for p in plans if search_term.lower() in p.goal.lower()]

    # Sorting
    if sort_by == "Newest":
        filtered_plans = sorted(filtered_plans, key=lambda x: x.created_at, reverse=True)
    elif sort_by == "Oldest":
        filtered_plans = sorted(filtered_plans, key=lambda x: x.created_at)
    elif sort_by == "Goal A-Z":
        filtered_plans = sorted(filtered_plans, key=lambda x: x.goal)
    elif sort_by == "Goal Z-A":
        filtered_plans = sorted(filtered_plans, key=lambda x: x.goal, reverse=True)

    st.markdown(f"**Found {len(filtered_plans)} plan(s)**")

    # Display plans
    for plan in filtered_plans:
        with st.expander(f"📋 {plan.goal[:50]}{'...' if len(plan.goal) > 50 else ''} - {plan.created_at.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**Goal:** {plan.goal}")
                st.markdown(f"**Created:** {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Status:** {plan.status}")
                
                # Display full AI output directly
                full_result = plan.get_enriched_info_dict().get('research_data', 'No AI output available')
                st.text(full_result)

            with col2:
                if st.button("👁️ View", key=f"view_{plan.id}"):
                    st.session_state.current_plan = {
                        'goal': plan.goal,
                        'full_result': full_result
                    }
                    st.rerun()
                if st.button("🗑️ Delete", key=f"delete_{plan.id}"):
                    db = SessionLocal()
                    try:
                        db.query(TaskPlan).filter(TaskPlan.id == plan.id).delete()
                        db.commit()
                        st.success("Plan deleted!")
                        st.rerun()
                    finally:
                        db.close()


if __name__ == "__main__":
    main()
