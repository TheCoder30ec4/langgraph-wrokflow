from typing import Dict, List, TypedDict, Annotated, Sequence
import os
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import nodes modules
# Note: These are placeholder imports. The actual implementations need to be completed in each file.
from webScrapingNode import scrape_website
from stepsGenrationNode import generate_steps
from testCaseGenrationNode import generate_test_cases
from sceneGenrationNode import generate_scenes
from videoExecutionScript import execute_video

# Define the state schema
class WorkflowState(TypedDict):
    link: str
    wrong_code: str
    problem_description: str
    test_cases: List[str]
    steps: List[str]
    scenes: List[str]
    video_path: str
    error: str

# Define the workflow graph
def create_workflow() -> StateGraph:
    """
    Create a workflow graph that connects all nodes for generating an explanatory video.
    
    Returns:
        StateGraph: The workflow graph
    """
    # Initialize the graph
    workflow = StateGraph(WorkflowState)
    
    # Define nodes
    
    # Web scraping node - extracts problem description and test cases from a link
    def web_scraping(state: WorkflowState) -> WorkflowState:
        try:
            result = scrape_website(state["link"])
            return {
                "problem_description": result["question"],
                "test_cases": result["test_cases"]
            }
        except Exception as e:
            return {"error": f"Error in web scraping: {str(e)}"}
    
    # Steps generation node - breaks down the solution into explanation steps
    def steps_generation(state: WorkflowState) -> WorkflowState:
        try:
            steps = generate_steps(state["wrong_code"])
            return {"steps": steps}
        except Exception as e:
            return {"error": f"Error in steps generation: {str(e)}"}
    
    # Test case generation node - generates test cases for the solution
    def test_case_generation(state: WorkflowState) -> WorkflowState:
        try:
            test_cases = generate_test_cases(state["wrong_code"])
            return {"test_cases": test_cases}
        except Exception as e:
            return {"error": f"Error in test case generation: {str(e)}"}
    
    # Scene generation node - converts explanation steps into animation scenes
    def scene_generation(state: WorkflowState) -> WorkflowState:
        try:
            scenes = generate_scenes(state["steps"])
            return {"scenes": scenes}
        except Exception as e:
            return {"error": f"Error in scene generation: {str(e)}"}
    
    # Video execution node - generates the final video
    def video_execution(state: WorkflowState) -> WorkflowState:
        try:
            video_path = execute_video(state["scenes"])
            return {"video_path": video_path}
        except Exception as e:
            return {"error": f"Error in video execution: {str(e)}"}
    
    # Error checking node
    def check_error(state: WorkflowState) -> WorkflowState:
        if "error" in state and state["error"]:
            print(f"Workflow error: {state['error']}")
            # Return the state to propagate the error
            return state
        # Return the state to continue the workflow
        return state
    
    # Add nodes to workflow
    workflow.add_node("web_scraping", web_scraping)
    workflow.add_node("steps_generation", steps_generation)
    workflow.add_node("test_case_generation", test_case_generation)
    workflow.add_node("scene_generation", scene_generation)
    workflow.add_node("video_execution", video_execution)
    workflow.add_node("check_error_web", check_error)
    workflow.add_node("check_error_steps", check_error)
    workflow.add_node("check_error_test", check_error)
    workflow.add_node("check_error_scene", check_error)
    workflow.add_node("check_error_video", check_error)
    
    # Define edges
    
    # Set the entry point
    workflow.set_entry_point("web_scraping")
    
    # Start with web scraping
    workflow.add_edge("web_scraping", "check_error_web")
    workflow.add_conditional_edges(
        "check_error_web",
        lambda state: "error" if state.get("error") else "continue",
        {
            "error": END,
            "continue": "steps_generation"
        }
    )
    
    # Generate steps
    workflow.add_edge("steps_generation", "check_error_steps")
    workflow.add_conditional_edges(
        "check_error_steps",
        lambda state: "error" if state.get("error") else "continue",
        {
            "error": END,
            "continue": "test_case_generation"
        }
    )
    
    # Generate test cases
    workflow.add_edge("test_case_generation", "check_error_test")
    workflow.add_conditional_edges(
        "check_error_test",
        lambda state: "error" if state.get("error") else "continue",
        {
            "error": END,
            "continue": "scene_generation"
        }
    )
    
    # Generate scenes
    workflow.add_edge("scene_generation", "check_error_scene")
    workflow.add_conditional_edges(
        "check_error_scene",
        lambda state: "error" if state.get("error") else "continue",
        {
            "error": END,
            "continue": "video_execution"
        }
    )
    
    # Execute video
    workflow.add_edge("video_execution", "check_error_video")
    workflow.add_conditional_edges(
        "check_error_video",
        lambda state: "error" if state.get("error") else "continue",
        {
            "error": END,
            "continue": END
        }
    )
    
    # Compile the graph
    return workflow.compile()

# Function to run the workflow
def run_workflow(link: str, wrong_code: str) -> Dict:
    """
    Run the explanatory video generation workflow.
    
    Args:
        link (str): The URL of the coding problem
        wrong_code (str): The incorrect code solution
        
    Returns:
        Dict: The final state of the workflow
    """
    # Create the workflow
    workflow = create_workflow()
    
    # Initialize the state
    initial_state = {
        "link": link,
        "wrong_code": wrong_code,
        "problem_description": "",
        "test_cases": [],
        "steps": [],
        "scenes": [],
        "video_path": "",
        "error": ""
    }
    
    # Run the workflow
    result = workflow.invoke(initial_state)
    
    return result
