# input: steps: [str]
# output: scenes: [[scene1: code], [scene2: code], [scene3: code], ....]
from typing import List
import os
from dotenv import load_dotenv
import re
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import List

# Load environment variables
load_dotenv()

# Configure the Groq API
groq_api_key = os.getenv("GROQ_API_KEY")

def generate_scenes(steps: List[str]) -> List[str]:
    """
    Generate Manim animation scenes for each explanation step.
    
    Args:
        steps (List[str]): List of explanation steps
        
    Returns:
        List[str]: List of Manim scene code for each step
    """
    try:
        # Define the response schema for structured output
        response_schemas = [
            ResponseSchema(name="scene_code", description="Python code for a Manim animation scene", type="str")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        # Create a ChatGroq instance
        chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mistral-saba-24B")
        
        # Generate a scene for each step
        scenes = []
        
        for i, step in enumerate(steps):
            # Prompt for the model to generate a Manim scene
            prompt = PromptTemplate(
                template="""
                Create a Manim animation scene that visualizes the following explanation step:
                
                "{step}"
                
                The scene should:
                1. Use Manim's animation capabilities to clearly illustrate the concepts
                2. Include appropriate text explanations
                3. Use visual elements like arrows, highlights, or color changes to emphasize important points
                4. Be self-contained and executable as a Python class that extends Scene from Manim
                
                Return ONLY the Python code for the scene, with proper imports and a complete class definition.
                The class should be named Step{step_number}Scene and should extend Scene from manim.
                
                Use manim-dsa for data structure visualizations if appropriate.
                Make sure the code is complete, properly indented, and ready to be executed.
                
                Return the information in the following format:
                {format_instructions}
                """,
                input_variables=["step"],
                partial_variables={"format_instructions": format_instructions, "step_number": i+1}
            )
            
            # Format the prompt with the step
            formatted_prompt = prompt.format(step=step)
            
            # Generate the response
            messages = [HumanMessage(content=formatted_prompt)]
            response = chat.invoke(messages)
            content = response.content
            
            # Parse the response
            try:
                structured_output = output_parser.parse(content)
                scene_code = structured_output["scene_code"]
            except Exception as e:
                print(f"Error parsing structured output for scene {i+1}: {str(e)}")
                # Fallback to manual extraction if parsing fails
                code_match = re.search(r'```(?:python)?\s*([\s\S]*?)\s*```', content)
                if code_match:
                    scene_code = code_match.group(1)
                else:
                    scene_code = content
                
                scene_code = scene_code.strip()
            
            # Add the scene to the list
            scenes.append(scene_code)
        
        return scenes
    
    except Exception as e:
        print(f"Error generating scenes: {str(e)}")
        # Return a basic scene in case of error
        return ["""
from manim import *

class ErrorScene(Scene):
    def construct(self):
        text = Text("Error generating animation")
        self.play(Write(text))
        self.wait(2)
        """]

# Example usage
if __name__ == "__main__":
    sample_steps = [
        "Step 1: The current code uses a nested loop to check all pairs of numbers, which is inefficient with O(n²) time complexity.",
        "Step 2: A more efficient approach is to use a hash map to store previously seen numbers and their indices."
    ]
    
    scenes = generate_scenes(sample_steps)
    print("Generated Scenes:")
    for i, scene in enumerate(scenes):
        print(f"Scene {i+1}:")
        print(scene)
        print("\n" + "-"*50 + "\n")
