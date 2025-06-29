
from manim import *
import sys
import os

# Add scenes directory to path
# Get the directory of the current script (render_all_scenes.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
scenes_path = os.path.join(script_dir, 'scenes')
sys.path.append(scenes_path)

# Import all scene classes
from step_1_scene import Step1Scene

# Configure Manim
# Set media directory relative to the script
config.media_dir = os.path.join(script_dir, 'media')
config.flush_cache = True

# Render all scenes
if __name__ == "__main__":
    scenes = [
        Step1Scene,

    ]
    
    for scene_class in scenes:
        scene = scene_class()
        scene.render()
    
    print("All scenes rendered successfully!")
