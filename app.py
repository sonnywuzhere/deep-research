"""
Streamlit App for Deep Research
A user-friendly interface for conducting deep research using OpenAI's API.

This app follows the EXACT flow from deep_research_clone.py:
1. setup_openai_client() - Initialize OpenAI client
2. generate_clarifying_questions() - Generate 5 clarifying questions
3. User provides answers
4. generate_research_plan() - Generate research goal and initial queries
5. conduct_research_iteratively() - Iterative research loop:
   - run_search() for each query
   - evaluate_research_completeness() after each batch
   - generate_additional_queries() if incomplete
   - Repeat until complete
6. generate_final_report() - Generate comprehensive report
"""

import streamlit as st
import deep_research_clone as drc
import warnings
import logging

# Suppress Streamlit's ScriptRunContext warning (harmless warning during initialization)
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# Also suppress in Streamlit's logger if it uses logging
logging.getLogger("streamlit.runtime.scriptrunner").setLevel(logging.ERROR)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Deep Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HELPER FUNCTION FOR SECRETS
# ============================================================================

def get_secret(key, default=""):
    """
    Safely get a secret from st.secrets without raising errors.
    Handles missing ScriptRunContext gracefully.
    
    Args:
        key (str): The secret key to retrieve
        default (str): Default value if secret is not found
    
    Returns:
        str: The secret value or default
    """
    try:
        # Try to access secrets - this will work when Streamlit context is available
        if hasattr(st, 'secrets'):
            try:
                return st.secrets.get(key, default)
            except Exception:
                # StreamlitSecretNotFoundError or missing ScriptRunContext
                return default
    except Exception:
        # Any other error accessing st.secrets
        pass
    return default

# ============================================================================
# SIDEBAR - API KEY CONFIGURATION
# (Moved to main interface to ensure proper context)
# ============================================================================


# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

def init_session_state():
    """Initialize all session state variables matching the flow."""
    # Check if we're in a Streamlit context before accessing session_state
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx is None:
            return  # Not in Streamlit context yet
    except (ImportError, AttributeError):
        # Older Streamlit versions or context not available
        pass
    
    defaults = {
        'step': 'topic_input',
        'topic': '',
        'client': None,
        'questions': [],
        'questions_response_id': None,
        'answers': [],
        'goal': '',
        'queries': [],
        'goal_response_id': None,
        'collected_data': [],
        'report': '',
        'research_iteration': 0,
        'current_queries': [],
        'is_research_complete': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def reset_session():
    """Reset all session state variables to initial state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def initialize_client(api_key):
    """
    Initialize OpenAI client - matches deep_research_clone.py setup_openai_client()
    """
    try:
        st.session_state.client = drc.setup_openai_client(api_key)
        return True
    except Exception as e:
        st.error(f"Error initializing client: {str(e)}")
        return False


# ============================================================================
# MAIN APP INTERFACE
# ============================================================================

# Initialize session state first (now we're in proper Streamlit context)
init_session_state()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key. You can also set it as an environment variable OPENAI_API_KEY.",
        value=get_secret("OPENAI_API_KEY", "")
    )
    
    if not api_key and not get_secret("OPENAI_API_KEY", ""):
        st.warning("⚠️ Please enter your OpenAI API key to continue.")
    
    st.markdown("---")
    st.markdown("### 📖 Research Flow:")
    st.markdown("""
    **Step 1:** Enter research topic
    
    **Step 2:** `generate_clarifying_questions()` - Creates 5 questions
    
    **Step 3:** Answer the questions
    
    **Step 4:** `generate_research_plan()` - Creates goal & queries
    
    **Step 5:** `conduct_research_iteratively()`:
    - `run_search()` for each query
    - `evaluate_research_completeness()`
    - `generate_additional_queries()` if needed
    - Repeats until complete
    
    **Step 6:** `generate_final_report()` - Creates report
    """)

st.title("🔍 Deep Research Assistant")
st.markdown("Conduct comprehensive research with AI-powered web search and analysis.")

# Check API key
final_api_key = get_secret("OPENAI_API_KEY", "")
if not final_api_key:
    final_api_key = api_key

if not final_api_key:
    st.stop()

# ============================================================================
# STEP 1: TOPIC INPUT
# ============================================================================

if st.session_state.step == 'topic_input':
    st.header("📝 Step 1: Enter Research Topic")
    st.markdown("**Function:** User input (prepares for `setup_openai_client()`)")
    
    topic_input = st.text_input(
        "What would you like to research?",
        placeholder="e.g., vibe coding, quantum computing, sustainable energy...",
        value=st.session_state.topic,
        key="topic_input_field"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Next →", type="primary", disabled=not topic_input):
            if initialize_client(final_api_key):
                st.session_state.topic = topic_input
                st.session_state.step = 'generating_questions'
                st.rerun()
    
    with col2:
        if st.button("🔄 Reset"):
            reset_session()
            st.rerun()


# ============================================================================
# STEP 2: GENERATE CLARIFYING QUESTIONS
# ============================================================================

elif st.session_state.step == 'generating_questions':
    st.header("❓ Step 2: Generating Clarifying Questions")
    st.markdown("**Function:** `drc.generate_clarifying_questions(client, topic)`")
    
    with st.spinner("Generating 5 clarifying questions to understand your research needs..."):
        try:
            # Exact match to deep_research_clone.py: generate_clarifying_questions()
            questions, questions_response_id = drc.generate_clarifying_questions(
                st.session_state.client, 
                st.session_state.topic
            )
            
            st.session_state.questions = questions
            st.session_state.questions_response_id = questions_response_id
            st.session_state.step = 'answer_questions'
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            if st.button("← Back"):
                st.session_state.step = 'topic_input'
                st.rerun()


# ============================================================================
# STEP 3: ANSWER QUESTIONS
# ============================================================================

elif st.session_state.step == 'answer_questions':
    st.header("💬 Step 3: Answer Clarifying Questions")
    st.markdown("**Function:** User input (prepares for `generate_research_plan()`)")
    st.info("Please answer the following questions to help us understand your research needs better.")
    
    # Initialize answers list if needed
    if len(st.session_state.answers) != len(st.session_state.questions):
        st.session_state.answers = [''] * len(st.session_state.questions)
    
    # Display questions and answer inputs
    for i, question in enumerate(st.session_state.questions):
        if question.strip():  # Skip empty questions
            st.session_state.answers[i] = st.text_area(
                f"**Question {i+1}:** {question}",
                value=st.session_state.answers[i],
                key=f"answer_{i}",
                height=100
            )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("← Back"):
            st.session_state.step = 'topic_input'
            st.rerun()
    
    with col2:
        all_answered = all(answer.strip() for answer in st.session_state.answers if answer)
        if st.button("Start Research →", type="primary", disabled=not all_answered):
            st.session_state.step = 'generating_plan'
            st.rerun()


# ============================================================================
# STEP 4: GENERATE RESEARCH PLAN (GOAL & QUERIES)
# ============================================================================

elif st.session_state.step == 'generating_plan':
    st.header("📋 Step 4: Generating Research Plan")
    st.markdown("**Function:** `drc.generate_research_plan(client, topic, questions, answers, questions_response_id)`")
    
    with st.spinner("Generating research goal and initial search queries..."):
        try:
            # Exact match to deep_research_clone.py: generate_research_plan()
            goal, queries, goal_response_id = drc.generate_research_plan(
                st.session_state.client,
                st.session_state.topic,
                st.session_state.questions,
                st.session_state.answers,
                st.session_state.questions_response_id
            )
            
            # Store all state for iterative research
            st.session_state.goal = goal
            st.session_state.queries = queries
            st.session_state.goal_response_id = goal_response_id
            st.session_state.current_queries = queries.copy()  # Start with initial queries
            st.session_state.research_iteration = 0
            st.session_state.collected_data = []
            st.session_state.is_research_complete = False
            
            # Display goal and queries
            st.subheader("🎯 Research Goal")
            st.info(goal)
            
            st.subheader("📊 Initial Search Queries")
            for i, query in enumerate(queries, 1):
                st.write(f"{i}. {query}")
            
            st.session_state.step = 'conducting_research'
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating research plan: {str(e)}")
            if st.button("← Back"):
                st.session_state.step = 'answer_questions'
                st.rerun()


# ============================================================================
# STEP 5: CONDUCT ITERATIVE RESEARCH
# This matches conduct_research_iteratively() from deep_research_clone.py
# ============================================================================

elif st.session_state.step == 'conducting_research':
    st.header("🔬 Step 5: Conducting Iterative Research")
    st.markdown("""
    **Function:** `drc.conduct_research_iteratively(client, goal, queries, goal_response_id)`
    
    **Internal flow (matches deep_research_clone.py exactly):**
    1. For each query: `drc.run_search(client, query)` 
    2. After batch: `drc.evaluate_research_completeness(client, goal, collected_data)`
    3. If incomplete: `drc.generate_additional_queries(client, goal, collected_data, goal_response_id)`
    4. Repeat until evaluation returns True
    """)
    
    progress_container = st.container()
    status_container = st.container()
    results_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Get current state (matches the loop in conduct_research_iteratively)
        collected = st.session_state.collected_data.copy()
        queries = st.session_state.current_queries.copy()
        iteration = st.session_state.research_iteration
        goal = st.session_state.goal
        goal_response_id = st.session_state.goal_response_id
        
        # Show current iteration
        with status_container:
            st.info(f"🔄 Research Iteration: {iteration + 1}")
            if queries:
                st.write(f"**Executing {len(queries)} search queries in this batch...**")
        
        # Execute all queries in current batch
        # This matches: for q in queries: collected.append(run_search(client, q))
        for i, q in enumerate(queries):
            status_text.text(f"🌐 Searching ({i+1}/{len(queries)}): {q}")
            progress_bar.progress((i + 1) / len(queries) * 0.4)  # 0-40% for searches
            
            # Exact match to deep_research_clone.py: run_search()
            search_result = drc.run_search(st.session_state.client, q)
            collected.append(search_result)
        
        # Update collected data
        st.session_state.collected_data = collected
        
        # Evaluate completeness
        # This matches: if evaluate_research_completeness(client, goal, collected): break
        progress_bar.progress(0.5)
        status_text.text("🔍 Evaluating research completeness...")
        
        is_complete = drc.evaluate_research_completeness(
            st.session_state.client,
            goal,
            collected
        )
        
        progress_bar.progress(0.6)
        st.session_state.is_research_complete = is_complete
        
        # Display results
        with results_container:
            st.success(f"✅ Completed {len(collected)} total searches across {iteration + 1} iteration(s)")
            with st.expander(f"View search results from iteration {iteration + 1}", expanded=False):
                for idx, result in enumerate(collected[-len(queries):], 1):
                    st.write(f"**Query {idx}:** {result['query']}")
                    st.text_area(
                        "Result", 
                        result['research_output'], 
                        height=100, 
                        key=f"result_{iteration}_{idx}",
                        disabled=True
                    )
        
        if is_complete:
            # Research is complete - matches the break in conduct_research_iteratively
            progress_bar.progress(1.0)
            status_text.text("✅ Research complete! All information gathered. Generating final report...")
            st.session_state.step = 'generating_report'
            st.rerun()
        else:
            # Research incomplete - generate additional queries
            # This matches: queries = generate_additional_queries(client, goal, collected, goal_response_id)
            progress_bar.progress(0.7)
            status_text.text("📝 Research incomplete. Generating additional queries...")
            
            # Exact match to deep_research_clone.py: generate_additional_queries()
            new_queries = drc.generate_additional_queries(
                st.session_state.client,
                goal,
                collected,
                goal_response_id
            )
            
            # Update for next iteration
            st.session_state.current_queries = new_queries
            st.session_state.research_iteration = iteration + 1
            
            with results_container:
                st.warning(f"⚠️ Research not yet complete. Generated {len(new_queries)} additional queries for next iteration.")
                with st.expander("View new queries for next iteration", expanded=False):
                    for i, query in enumerate(new_queries, 1):
                        st.write(f"{i}. {query}")
            
            # Continue to next iteration (matches the loop in conduct_research_iteratively)
            st.session_state.step = 'conducting_research'
            st.rerun()
        
    except Exception as e:
        st.error(f"Error during research: {str(e)}")
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())
        if st.button("← Back"):
            st.session_state.step = 'generating_plan'
            st.rerun()


# ============================================================================
# STEP 6: GENERATE FINAL REPORT
# ============================================================================

elif st.session_state.step == 'generating_report':
    st.header("📝 Step 6: Generating Final Report")
    st.markdown("**Function:** `drc.generate_final_report(client, goal, collected_data)`")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        progress_bar.progress(0.3)
        status_text.text("📝 Writing comprehensive research report with citations...")
        
        # Exact match to deep_research_clone.py: generate_final_report()
        final_report = drc.generate_final_report(
            st.session_state.client,
            st.session_state.goal,
            st.session_state.collected_data
        )
        
        st.session_state.report = final_report
        progress_bar.progress(1.0)
        status_text.text("✅ Report generated!")
        
        st.session_state.step = 'display_report'
        st.rerun()
        
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        import traceback
        with st.expander("Error details"):
            st.code(traceback.format_exc())
        if st.button("← Back"):
            st.session_state.step = 'conducting_research'
            st.rerun()


# ============================================================================
# STEP 7: DISPLAY FINAL REPORT
# ============================================================================

elif st.session_state.step == 'display_report':
    st.header("📄 Final Research Report")
    st.markdown("**Function:** Display results (research complete)")
    
    # Display goal
    st.subheader("🎯 Research Goal")
    st.info(st.session_state.goal)
    
    # Display research summary
    with st.expander("📊 Research Summary", expanded=True):
        st.write(f"**Topic:** {st.session_state.topic}")
        st.write(f"**Total Search Queries Executed:** {len(st.session_state.collected_data)}")
        st.write(f"**Research Iterations:** {st.session_state.research_iteration + 1}")
        st.write(f"**Research Status:** {'✅ Complete' if st.session_state.is_research_complete else '⚠️ Incomplete'}")
    
    # Display report
    st.subheader("📊 Research Report")
    st.markdown(st.session_state.report)
    
    # Download button
    st.download_button(
        label="📥 Download Report (Markdown)",
        data=st.session_state.report,
        file_name=f"research_report_{st.session_state.topic.replace(' ', '_')}.md",
        mime="text/markdown"
    )
    
    # Reset button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 New Research", type="primary"):
            reset_session()
            st.rerun()
