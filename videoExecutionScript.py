# input: scenes: [[scene1: code], [scene2: code], [scene3: code], ....]
# output: file creation and running the using subprocess.....
import os
import subprocess
import shutil
from typing import List
import datetime

def execute_video(scenes: List[str]) -> str:
    """
    Save scene code to files and execute Manim to generate the final video.
    
    Args:
        scenes (List[str]): List of Manim scene code strings
        
    Returns:
        str: Path to the generated video file
    """
    try:
        # Create a timestamp for unique folder naming
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"output_video_{timestamp}"
        scenes_dir = os.path.join(output_dir, "scenes")
        
        # Create output directories
        os.makedirs(scenes_dir, exist_ok=True)
        
        # Save each scene to a separate file
        scene_files = []
        for i, scene_code in enumerate(scenes):
            scene_file = os.path.join(scenes_dir, f"step_{i+1}_scene.py")
            with open(scene_file, "w") as f:
                f.write(scene_code)
            scene_files.append(scene_file)
        
        # Create a main file that imports and renders all scenes
        main_file_content = """
from manim import *
import sys
import os

# Add scenes directory to path
# Get the directory of the current script (render_all_scenes.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
scenes_path = os.path.join(script_dir, 'scenes')
sys.path.append(scenes_path)

# Import all scene classes
"""
        for i in range(len(scenes)):
            main_file_content += f"from step_{i+1}_scene import Step{i+1}Scene\n"
        
        main_file_content += """
# Configure Manim
# Set media directory relative to the script
config.media_dir = os.path.join(script_dir, 'media')
config.flush_cache = True

# Render all scenes
if __name__ == "__main__":
    scenes = [
"""
        for i in range(len(scenes)):
            main_file_content += f"        Step{i+1}Scene,\n"
        
        main_file_content += """
    ]
    
    for scene_class in scenes:
        scene = scene_class()
        scene.render()
    
    print("All scenes rendered successfully!")
"""
        
        # Save the main file
        main_file = os.path.join(output_dir, "render_all_scenes.py")
        with open(main_file, "w") as f:
            f.write(main_file_content)
        
        # Execute Manim to render the scenes
        print("Rendering Manim scenes...")
        render_command = ["manim", main_file, "-pql"]
        result = subprocess.run(render_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error rendering scenes: {result.stderr}")
            raise Exception(f"Manim rendering failed: {result.stderr}")
        
        # Find the rendered video files
        media_dir = os.path.join(output_dir, "media", "videos")
        video_files = []
        
        if os.path.exists(media_dir):
            for root, _, files in os.walk(media_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        video_files.append(os.path.join(root, file))
        
        if not video_files:
            raise Exception("No video files were generated")
        
        # If there are multiple videos, concatenate them
        if len(video_files) > 1:
            # Create a file list for ffmpeg
            concat_list_file = os.path.join(output_dir, "concat_list.txt")
            with open(concat_list_file, "w") as f:
                for video_file in video_files:
                    f.write(f"file '{video_file}'\n")
            
            # Concatenate videos using ffmpeg
            final_video_path = os.path.join(output_dir, f"final_video_{timestamp}.mp4")
            concat_command = [
                "ffmpeg", "-f", "concat", "-safe", "0", 
                "-i", concat_list_file, "-c", "copy", final_video_path
            ]
            result = subprocess.run(concat_command, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error concatenating videos: {result.stderr}")
                raise Exception(f"Video concatenation failed: {result.stderr}")
            
            return final_video_path
        else:
            # If there's only one video, return its path
            return video_files[0]
    
    except Exception as e:
        print(f"Error executing video generation: {str(e)}")
        return ""

# Example usage
if __name__ == "__main__":
    sample_scenes = [
        '''
from manim import *

class Step1Scene(Scene):
    def construct(self):
        title = Text("Two Sum Problem - Inefficient Solution")
        self.play(Write(title))
        self.wait(2)
        ''',
        '''
from manim import *

class Step2Scene(Scene):
    def construct(self):
        title = Text("Efficient Solution with Hash Map")
        self.play(Write(title))
        self.wait(2)
        '''
    ]
    
    video_path = execute_video(sample_scenes)
    print(f"Video generated at: {video_path}")
