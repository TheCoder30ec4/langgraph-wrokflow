# input: code: str 
# output: steps : [str]
from typing import List
import os
from dotenv import load_dotenv
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import List

# Load environment variables
load_dotenv()

# Configure the Groq API
groq_api_key = os.getenv("GROQ_API_KEY")

def generate_steps(code: str) -> List[str]:
    """
    Generate explanation steps for the given code, identifying issues and how to fix them.
    
    Args:
        code (str): The code to analyze (potentially incorrect)
        
    Returns:
        List[str]: A list of explanation steps
    """
    try:
        # Define the response schema for structured output
        response_schemas = [
            ResponseSchema(name="steps", description="List of explanation steps for code analysis", type="List[str]")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
         # Create a ChatGroq instance
        chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mistral-saba-24B")
        
        # Prompt for the model to analyze the code and generate steps
        prompt = PromptTemplate(
            template="""
            Analyze the following code which may contain errors or inefficiencies:
            
            ```
            {code}
            ```
            
            Generate a detailed step-by-step explanation that:
            1. Identifies any issues or bugs in the code
            2. Explains why these issues are problematic
            3. Provides a clear solution for each issue
            4. Explains the correct approach
            
            Format your response as a list of distinct steps, with each step focusing on a specific aspect of the code.
            Each step should be comprehensive but concise.
            
            Return the information in the following format:
            {format_instructions}
            """,
            input_variables=["code"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        # Format the prompt with the code
        formatted_prompt = prompt.format(code=code)
        
        # Generate the response
        messages = [HumanMessage(content=formatted_prompt)]
        response = chat.invoke(messages)
        content = response.content
        
        # Parse the response
        structured_output = output_parser.parse(content)
        return structured_output["steps"]
    
    except Exception as e:
        print(f"Error generating steps: {str(e)}")
        # Return a basic step in case of error
        return ["Error analyzing the code. Please check if the code is valid and try again."]

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
    
    steps = generate_steps(sample_code)
    print("Generated Steps:")
    for i, step in enumerate(steps):
        print(f"Step {i+1}:")
        print(step)
        print()
