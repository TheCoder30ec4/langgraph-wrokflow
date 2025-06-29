import unittest
import os
import sys
import shutil

# Add the parent directory to the path so we can import from workflow
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow import run_workflow

class TestExplanatoryVideoWorkflow(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_output_dir = "test_output"
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
    
    def test_full_workflow(self):
        """Test the full workflow with a sample problem and wrong code."""
        link = "https://leetcode.com/problems/two-sum/"
        wrong_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None
"""
        
        # Run the workflow
        result = run_workflow(link, wrong_code)
        
        # Check if the workflow completed without errors
        self.assertFalse(result.get("error"), f"Workflow failed with error: {result.get('error')}")
        
        # Check if problem description was extracted
        self.assertTrue(result.get("problem_description"), "No problem description extracted")
        self.assertNotEqual(result.get("problem_description"), "", "Problem description is empty")
        
        # Check if test cases were extracted or generated
        self.assertTrue(result.get("test_cases"), "No test cases extracted or generated")
        self.assertIsInstance(result.get("test_cases"), list, "Test cases should be a list")
        self.assertGreater(len(result.get("test_cases")), 0, "Test cases list is empty")
        
        # Check if steps were generated
        self.assertTrue(result.get("steps"), "No steps generated")
        self.assertIsInstance(result.get("steps"), list, "Steps should be a list")
        self.assertGreater(len(result.get("steps")), 0, "Steps list is empty")
        
        # Check if scenes were generated
        self.assertTrue(result.get("scenes"), "No scenes generated")
        self.assertIsInstance(result.get("scenes"), list, "Scenes should be a list")
        self.assertGreater(len(result.get("scenes")), 0, "Scenes list is empty")
        
        # Check if video was generated (this might be skipped in a test environment)
        # Uncomment the following lines if you want to test video generation
        # self.assertTrue(result.get("video_path"), "No video path returned")
        # self.assertNotEqual(result.get("video_path"), "", "Video path is empty")
        # self.assertTrue(os.path.exists(result.get("video_path")), "Video file does not exist")
    
    def test_invalid_link(self):
        """Test the workflow with an invalid link."""
        link = "https://invalid-url-that-does-not-exist.com"
        wrong_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None
"""
        
        # Run the workflow
        result = run_workflow(link, wrong_code)
        
        # Check if the workflow handled the error gracefully
        self.assertTrue(result.get("error"), "Workflow should report an error for invalid link")
        self.assertIn("scraping", result.get("error").lower(), "Error message should mention scraping issue")
    
    def test_invalid_code(self):
        """Test the workflow with invalid code syntax."""
        link = "https://leetcode.com/problems/two-sum/"
        wrong_code = """
def two_sum(nums, target)
    for i in range(len(nums)):
        for j in range(len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None
"""
        
        # Run the workflow
        result = run_workflow(link, wrong_code)
        
        # Check if the workflow continues despite invalid code syntax
        # The system should still generate steps pointing out the syntax error
        self.assertFalse(result.get("error"), f"Workflow failed with error: {result.get('error')}")
        self.assertTrue(result.get("steps"), "No steps generated for invalid code")
        self.assertGreater(len(result.get("steps")), 0, "Steps list is empty for invalid code")

if __name__ == '__main__':
    unittest.main()
