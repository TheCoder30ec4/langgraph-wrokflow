import argparse
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "langgraph-wrokflow"))
from  workflow import run_workflow
from fastapi import FastAPI

def main():
    """
    Main function to run the explanatory video generation workflow.
    """
    parser = argparse.ArgumentParser(description="Generate an explanatory video for a coding problem")
    parser.add_argument("--link", type=str, required=True, help="URL of the coding problem")
    parser.add_argument("--wrong-code", type=str, required=True, help="Incorrect code solution to analyze")
    
    args = parser.parse_args()
    
    print(f"Generating explanatory video for problem at: {args.link}")
    print("Analyzing provided code...")
    
    # Run the workflow
    result = run_workflow(args.link, args.wrong_code)
    
    if result.get("error"):
        print(f"Error in workflow: {result['error']}")
    elif result.get("video_path"):
        print(f"Video successfully generated at: {result['video_path']}")
    else:
        print("Workflow completed but no video path was returned.")
    
    return result

if __name__ == "__main__":
    main()
