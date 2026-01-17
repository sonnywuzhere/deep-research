"""
Deep Research Clone - Modular Research System
This module provides functions for conducting deep research using OpenAI's API.
"""

from openai import OpenAI
import os
import json
import itertools


# ============================================================================
# CONFIGURATION MODULE
# ============================================================================

def setup_openai_client(api_key=None):
    """
    Initialize and configure the OpenAI client.
    
    Args:
        api_key (str, optional): OpenAI API key. If None, reads from environment variable.
    
    Returns:
        OpenAI: Configured OpenAI client instance
    """
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    elif not os.environ.get('OPENAI_API_KEY'):
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
    
    return OpenAI()


# Model configuration constants
MODEL = "gpt-4.1"
MODEL_MINI = "gpt-4.1-mini"
TOOLS = [{"type": "web_search"}]

# Developer message for AI instructions
DEVELOPER_MESSAGE = """
You are an expert Deep Researcher.
You provide complete and in depth research to the user.
"""


# ============================================================================
# QUESTION GENERATION MODULE
# ============================================================================

def generate_clarifying_questions(client, topic):
    """
    Generate 5 clarifying questions about the research topic.
    
    Step-by-step:
    1. Creates a prompt asking for 5 numbered clarifying questions
    2. Uses OpenAI API to generate questions that help understand research purpose
    3. Parses the response to extract individual questions
    
    Args:
        client (OpenAI): Initialized OpenAI client
        topic (str): The research topic
    
    Returns:
        tuple: (questions_list, response_id) - List of questions and API response ID
    """
    prompt_to_clarify = f"""
Ask 5 numbered clarifying question to the user about the topic: {topic}.
The goal os the questions is to understand the intended purpose of the research.
Reply only with the questions
"""
    
    clarify = client.responses.create(
        model=MODEL_MINI,
        input=prompt_to_clarify,
        instructions=DEVELOPER_MESSAGE
    )
    
    questions = clarify.output[0].content[0].text.split("\n")
    questions = [q.strip() for q in questions if q.strip()]  # Clean up empty lines
    
    return questions, clarify.id


# ============================================================================
# GOAL AND QUERY GENERATION MODULE
# ============================================================================

def generate_research_plan(client, topic, questions, answers, previous_response_id=None):
    """
    Generate research goal and search queries based on user answers.
    
    Step-by-step:
    1. Creates a prompt combining topic, questions, and user answers
    2. Asks the AI to generate a research goal and 5 web search queries
    3. Parses JSON response to extract goal and queries
    
    Args:
        client (OpenAI): Initialized OpenAI client
        topic (str): The research topic
        questions (list): List of clarifying questions asked
        answers (list): List of user answers to those questions
        previous_response_id (str, optional): Previous API response ID for context
    
    Returns:
        tuple: (goal, queries_list, response_id) - Research goal, list of queries, and API response ID
    """
    prompt_goals = f"""
Using the user answers {answers} to que questions {questions}, write a goal sentence and 5 web search queries for the research about {topic}
Output: A json list of the goal and the 5 web search queries that will reach it.
Format: {{"goal": "...", "queries": ["q1", ....]}}
"""
    
    kwargs = {
        "model": MODEL,
        "input": prompt_goals,
        "instructions": DEVELOPER_MESSAGE
    }
    
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id
    
    goal_and_queries = client.responses.create(**kwargs)
    
    plan_text = goal_and_queries.output[0].content[0].text
    plan = json.loads(plan_text)
    
    goal = plan["goal"]
    queries = plan["queries"]
    
    return goal, queries, goal_and_queries.id


# ============================================================================
# WEB SEARCH MODULE
# ============================================================================

def run_search(client, query):
    """
    Execute a web search query using OpenAI's web search tool.
    
    Step-by-step:
    1. Formats the query with "search:" prefix
    2. Calls OpenAI API with web_search tool enabled
    3. Extracts search results from the response
    4. Returns query, response ID, and research output
    
    Args:
        client (OpenAI): Initialized OpenAI client
        query (str): The search query to execute
    
    Returns:
        dict: Dictionary containing query, response_id, and research_output
    """
    web_search = client.responses.create(
        model=MODEL,
        input=f"search: {query}",
        instructions=DEVELOPER_MESSAGE,
        tools=TOOLS
    )
    
    return {
        "query": query,
        "resp_id": web_search.output[1].id,
        "research_output": web_search.output[1].content[0].text
    }


# ============================================================================
# EVALUATION MODULE
# ============================================================================

def evaluate_research_completeness(client, goal, collected_data):
    """
    Evaluate if the collected research data is sufficient to meet the goal.
    
    Step-by-step:
    1. Creates a prompt asking if collected information satisfies the research goal
    2. Uses OpenAI API to evaluate completeness
    3. Returns True if "yes" is in the response, False otherwise
    
    Args:
        client (OpenAI): Initialized OpenAI client
        goal (str): The research goal to evaluate against
        collected_data (list): List of research results collected so far
    
    Returns:
        bool: True if research is complete, False if more information is needed
    """
    review = client.responses.create(
        model=MODEL,
        input=[
            {"role": "developer", "content": f"Research goal: {goal}"},
            {"role": "assistant", "content": json.dumps(collected_data)},
            {"role": "user", "content": "Does this information will fully satisfy the goal? Answer Yes or No only."}
        ],
        instructions=DEVELOPER_MESSAGE
    )
    
    return "yes" in review.output[0].content[0].text.lower()


def generate_additional_queries(client, goal, collected_data, previous_response_id):
    """
    Generate additional search queries when initial research is insufficient.
    
    Step-by-step:
    1. Creates a prompt with current research data and goal
    2. Asks AI to generate 5 more web search queries
    3. Parses JSON response to extract new queries
    
    Args:
        client (OpenAI): Initialized OpenAI client
        goal (str): The research goal
        collected_data (list): Current research results
        previous_response_id (str): Previous API response ID for context
    
    Returns:
        list: List of new search queries
    """
    more_searches = client.responses.create(
        model=MODEL,
        input=[
            {"role": "assistant", "content": f"Current data: {json.dumps(collected_data)}"},
            {"role": "user", "content": f"This has not met the goal: {goal}. Write 5 other web searchs to achieve the goal"}
        ],
        instructions=DEVELOPER_MESSAGE,
        previous_response_id=previous_response_id
    )
    
    queries_text = more_searches.output[0].content[0].text
    queries = json.loads(queries_text)
    
    return queries


# ============================================================================
# RESEARCH EXECUTION MODULE
# ============================================================================

def conduct_research_iteratively(client, goal, initial_queries, goal_response_id):
    """
    Conduct research iteratively until the goal is satisfied.
    
    Step-by-step:
    1. Starts with initial queries
    2. Executes all queries and collects results
    3. Evaluates if research is complete
    4. If not complete, generates additional queries and repeats
    5. Continues until evaluation returns True
    
    Args:
        client (OpenAI): Initialized OpenAI client
        goal (str): The research goal
        initial_queries (list): Initial list of search queries
        goal_response_id (str): Response ID from goal generation for context
    
    Returns:
        list: Complete list of research results
    """
    collected = []
    queries = initial_queries
    
    for iteration in itertools.count():
        # Execute all current queries
        for q in queries:
            collected.append(run_search(client, q))
        
        # Check if we have enough information
        if evaluate_research_completeness(client, goal, collected):
            break
        
        # Generate more queries if needed
        queries = generate_additional_queries(client, goal, collected, goal_response_id)
    
    return collected


# ============================================================================
# REPORT GENERATION MODULE
# ============================================================================

def generate_final_report(client, goal, collected_data):
    """
    Generate the final comprehensive research report.
    
    Step-by-step:
    1. Creates a prompt asking for a complete detailed report
    2. Includes instructions for inline citations [n] and reference list
    3. Uses all collected research data as input
    4. Returns formatted markdown report
    
    Args:
        client (OpenAI): Initialized OpenAI client
        goal (str): The research goal
        collected_data (list): All collected research results
    
    Returns:
        str: Final research report in markdown format
    """
    report = client.responses.create(
        model=MODEL,
        input=[
            {"role": "developer", "content": (
                f"Write a complete and detailed report about research goal: {goal}"
                "Cite Sources inline using [n] and append a reference "
                "list mapping [n] to url"
            )},
            {"role": "assistant", "content": json.dumps(collected_data)}
        ],
        instructions=DEVELOPER_MESSAGE
    )
    
    return report.output[0].content[0].text


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def run_deep_research(topic, answers, api_key=None):
    """
    Main function to execute the complete deep research process.
    
    Step-by-step execution flow:
    1. Setup OpenAI client
    2. Generate clarifying questions (if answers not provided)
    3. Generate research goal and initial queries
    4. Conduct iterative research until goal is met
    5. Generate final comprehensive report
    
    Args:
        topic (str): Research topic
        answers (list): List of answers to clarifying questions
        api_key (str, optional): OpenAI API key
    
    Returns:
        dict: Dictionary containing goal, questions, and final report
    """
    # Step 1: Setup
    client = setup_openai_client(api_key)
    
    # Step 2: Generate questions (for reference)
    questions, questions_response_id = generate_clarifying_questions(client, topic)
    
    # Step 3: Generate research plan
    goal, queries, goal_response_id = generate_research_plan(
        client, topic, questions, answers, questions_response_id
    )
    
    # Step 4: Conduct research iteratively
    collected_data = conduct_research_iteratively(client, goal, queries, goal_response_id)
    
    # Step 5: Generate final report
    final_report = generate_final_report(client, goal, collected_data)
    
    return {
        "goal": goal,
        "questions": questions,
        "report": final_report
    }
