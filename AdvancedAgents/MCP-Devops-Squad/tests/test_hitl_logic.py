import unittest
import json
import os
from src.agents.janitor import JanitorAgent, CommandRequest

class TestHITLLogic(unittest.TestCase):
    def setUp(self):
        self.janitor = JanitorAgent()
        self.test_file = self.janitor.approval_file
        # Reset the file
        with open(self.test_file, "w") as f:
            json.dump([], f)

    def test_staging_sensitive_command(self):
        """Verify that sensitive commands are correctly staged in the JSON file."""
        command = "kill -9 9999"
        justification = "Cleanup test"
        resource_id = "test-resource"
        
        result = self.janitor.request_execution(command, justification, resource_id)
        
        self.assertEqual(result["status"], "pending_hitl")
        
        with open(self.test_file, "r") as f:
            approvals = json.load(f)
            
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0]["command"], command)
        self.assertEqual(approvals[0]["resource_id"], resource_id)

    def test_execution_of_approved_command(self):
        """Verify that the direct execution method works (mock mode)."""
        command = "ls -la"
        result = self.janitor.execute_approved_command(command)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["executed_command"], command)

if __name__ == "__main__":
    unittest.main()
