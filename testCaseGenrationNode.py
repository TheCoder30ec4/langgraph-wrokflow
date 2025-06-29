# Input: code: str 
# output: testCases: [[],[],[]...]
from typing import List, Any
import os
from dotenv import load_dotenv
import json
import re
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import List, Any

# Load environment variables
load_dotenv()

# Configure the Groq API
groq_api_key = os.getenv("GROQ_API_KEY")

def generate_test_cases(code: str) -> List[List[Any]]:
    """
    Generate test cases for the given code to demonstrate issues and solutions.
    
    Args:
        code (str): The code to generate test cases for
        
    Returns:
        List[List[Any]]: A list of test cases, where each test case is a list of inputs and expected outputs
    """
    try:
        # Extract function name and parameters from the code
        function_match = re.search(r'def\s+(\w+)\s*\((.*?)\):', code)
        if not function_match:
            raise ValueError("Could not identify function in the provided code")
        
        function_name = function_match.group(1)
        parameters = function_match.group(2).split(',')
        param_names = [p.strip().split(':')[0].split('=')[0].strip() for p in parameters]
        
        # Define the response schema for structured output
        response_schemas = [
            ResponseSchema(name="test_cases", description="List of test cases with inputs, expected output, actual output, and explanation", type="List[Dict]")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create a ChatGroq instance
        chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mistral-saba-24B")
        
        # Prompt for the model to generate test cases
        prompt = PromptTemplate(
            template="""
            Analyze the following code and generate test cases that will demonstrate both its issues and how it should work correctly:
            
            ```
            {code}
            ```
            
            The function name is '{function_name}' and it takes parameters: {param_names}.
            
            Generate 5 diverse test cases that:
            1. Include normal cases
            2. Include edge cases
            3. Include cases that specifically expose the bugs or inefficiencies in the code
            
            For each test case, provide:
            1. The input values for each parameter
            2. The expected output if the code was correct
            3. The actual output with the current code (if different)
            4. A brief explanation of what the test case demonstrates
            
            Format your response as a JSON array where each test case is an object with these fields:
            - inputs: an array of input values in the order of the function parameters
            - expected_output: the correct output
            - actual_output: what the buggy code would return
            - explanation: brief explanation of the test case
            
            Return the information in the following format:
            {format_instructions}
            """,
            input_variables=["code"],
            partial_variables={"format_instructions": format_instructions, "function_name": function_name, "param_names": ", ".join(param_names)}
        )
        
        # Format the prompt with the code
        formatted_prompt = prompt.format(code=code)
        
        # Generate the response
        messages = [HumanMessage(content=formatted_prompt)]
        response = chat.invoke(messages)
        content = response.content
        
        # Parse the response
        try:
            structured_output = output_parser.parse(content)
            test_cases_data = structured_output["test_cases"]
            
            # Convert the parsed data to the expected format
            formatted_test_cases = []
            
            for tc in test_cases_data:
                if isinstance(tc, dict):
                    test_case = []
                    
                    # Add inputs
                    if 'inputs' in tc:
                        test_case.append(tc['inputs'])
                    else:
                        test_case.append(["No input specified"])
                    
                    # Add expected output
                    if 'expected_output' in tc:
                        test_case.append(tc['expected_output'])
                    else:
                        test_case.append("No expected output specified")
                    
                    # Add explanation
                    if 'explanation' in tc:
                        test_case.append(tc['explanation'])
                    else:
                        test_case.append("No explanation provided")
                    
                    formatted_test_cases.append(test_case)
            
            return formatted_test_cases
        except Exception as e:
            print(f"Error parsing structured output: {str(e)}")
            # Fallback to manual parsing if structured parsing fails
            
            # Extract JSON from the response (it might be wrapped in markdown code blocks)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content
            
            # Clean up the JSON string
            json_str = json_str.strip()
            
            # Try to parse the JSON
            try:
                test_cases_data = json.loads(json_str)
                if isinstance(test_cases_data, dict) and "test_cases" in test_cases_data:
                    test_cases_data = test_cases_data["test_cases"]
                
                # Convert the parsed data to the expected format
                formatted_test_cases = []
                
                for tc in test_cases_data:
                    if isinstance(tc, dict):
                        test_case = []
                        
                        # Add inputs
                        if 'inputs' in tc:
                            test_case.append(tc['inputs'])
                        else:
                            test_case.append(["No input specified"])
                        
                        # Add expected output
                        if 'expected_output' in tc:
                            test_case.append(tc['expected_output'])
                        else:
                            test_case.append("No expected output specified")
                        
                        # Add explanation
                        if 'explanation' in tc:
                            test_case.append(tc['explanation'])
                        else:
                            test_case.append("No explanation provided")
                        
                        formatted_test_cases.append(test_case)
                
                return formatted_test_cases
            except json.JSONDecodeError:
                print("Could not parse JSON response. Using simplified test cases.")
                return [
                    [["Sample input 1"], "Expected output 1", "This is a basic test case"],
                    [["Sample input 2"], "Expected output 2", "This is an edge case"]
                ]
    
    except Exception as e:
        print(f"Error generating test cases: {str(e)}")
        # Return basic test cases in case of error
        return [
            [["Sample input"], "Expected output", "Basic test case"],
            [["Edge case input"], "Expected output for edge case", "Edge case test"]
        ]

# Example usage
if __name__ == "__main__":
    sample_code = """
    def two_sum(nums, target):
        for i in range(len(nums)):
            for j in range(len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return None
    """
    
    test_cases = generate_test_cases(sample_code)
    print("Generated Test Cases:")
    for i, test_case in enumerate(test_cases):
        print(f"Test Case {i+1}:")
        print(f"Inputs: {test_case[0]}")
        print(f"Expected Output: {test_case[1]}")
        print(f"Explanation: {test_case[2]}")
        print()
