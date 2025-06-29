# Input: https://link.com 
# Output: question: str , test cases: [str]
from crewai_tools import ScrapeWebsiteTool
from typing import Dict, List
import re
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
# Input: https://link.com 
# Output: question: str , test cases: [str]
from crewai_tools import ScrapeWebsiteTool
from typing import Dict, List
import re
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Configure the Groq API
print(os.getenv("GROQ_API_KEY"))
groq_api_key = os.getenv("GROQ_API_KEY")

def scrape_website(url: str) -> Dict:
    """
    Scrape a coding problem website to extract the problem description and test cases.
    
    Args:
        url (str): The URL of the coding problem
        
    Returns:
        Dict: A dictionary containing the problem description and test cases
    """
    try:
        # Create a scraping tool for the given URL
        tool = ScrapeWebsiteTool(website_url=url)
        
        # Run the scraping tool to get the website content
        content = tool.run()
        
        # Define the response schemas for structured output
        response_schemas = [
            ResponseSchema(name="question", description="The problem description or question statement"),
            ResponseSchema(name="test_cases", description="List of test cases with input and output", type="List[str]")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create a ChatGroq instance
        chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mistral-saba-24B")
        
        # Prompt for structured extraction of content
        prompt = PromptTemplate(
            template="""
            Extract the problem description and test cases from the following scraped website content:
            
            {content}
            
            Return the information in the following format:
            {format_instructions}
            """,
            input_variables=["content"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        # Format the prompt with the scraped content
        formatted_prompt = prompt.format(content=content)
        
        # Generate the structured response
        messages = [HumanMessage(content=formatted_prompt)]
        response = chat.invoke(messages)
        content = response.content
        
        # Parse the response
        try:
            structured_output = output_parser.parse(content)
            return structured_output
        except Exception as e:
            print(f"Error parsing structured output: {str(e)}")
            # Fallback to manual extraction if parsing fails
            
            # Extract problem description - assuming it's the text before "Example" or "Examples"
            description_match = re.split(r'Example[s]?', content, 1)
            problem_description = description_match[0].strip() if len(description_match) > 1 else content
            
            # Extract test cases - assuming they're in the format "Input: ... Output: ..."
            test_cases = []
            examples = re.findall(r'Example \d+:(.*?)(?=Example \d+:|$)', content, re.DOTALL)
            if not examples:
                examples = re.findall(r'Input:(.*?)Output:(.*?)(?=Input:|$)', content, re.DOTALL)
                
            for example in examples:
                if isinstance(example, tuple):
                    input_text = example[0].strip()
                    output_text = example[1].strip()
                    test_cases.append(f"Input: {input_text}\nOutput: {output_text}")
                else:
                    input_match = re.search(r'Input:(.*?)Output:', example, re.DOTALL)
                    output_match = re.search(r'Output:(.*)', example, re.DOTALL)
                    
                    if input_match and output_match:
                        input_text = input_match.group(1).strip()
                        output_text = output_match.group(1).strip()
                        test_cases.append(f"Input: {input_text}\nOutput: {output_text}")
            
            return {
                "question": problem_description,
                "test_cases": test_cases
            }
    except Exception as e:
        print(f"Error scraping website: {str(e)}")
        # Return empty values in case of error
        return {
            "question": "",
            "test_cases": []
        }

# Example usage
if __name__ == "__main__":
    url = "https://leetcode.com/problems/two-sum/"
    result = scrape_website(url)
    print("Problem Description:")
    print(result["question"])
    print("\nTest Cases:")
    for i, test_case in enumerate(result["test_cases"]):
        print(f"Test Case {i+1}:")
        print(test_case)
        print()
