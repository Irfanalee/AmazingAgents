import unittest
import json
import os
from src.orchestrator.incident_runner import IncidentRunner

class TestSquadIntegration(unittest.TestCase):
    """Integration test for the full SRE Squad lifecycle using IncidentRunner."""
    
    def setUp(self):
        self.runner = IncidentRunner()
        self.resource_id = "integration-test-server"
        
        # Cleanup pending approvals
        if os.path.exists("config/pending_approvals.json"):
            with open("config/pending_approvals.json", "w") as f:
                json.dump([], f)

    def test_full_incident_lifecycle(self):
        """Simulate a full incident lifecycle from detection to remediation."""
        
        # Run the full loop
        final_context = self.runner.run(self.resource_id)
        
        # Verify the loop progressed
        # Step 1: Monitor detected high CPU (implicit in runner.run)
        # Step 2: Lead-SRE delegated to Debugger-Agent (mock step 0)
        # Step 3: Lead-SRE delegated to Sargent-Agent (mock step 1)
        # Step 4: Lead-SRE delegated to Janitor-Agent (mock step 2)
        # Step 5: Final iteration marked as resolved
        
        self.assertTrue(len(final_context.history) >= 3, f"History too short: {len(final_context.history)}")
        
        # Check first action was Debugger
        self.assertEqual(final_context.history[0].agent_name, "Debugger-Agent")
        self.assertIn("log_path", final_context.history[0].task_kwargs)
        
        # Check second action was Sargent
        self.assertEqual(final_context.history[1].agent_name, "Sargent-Agent")
        self.assertEqual(final_context.history[1].task_kwargs["scan_type"], "image")
        
        # Check third action was Janitor
        self.assertEqual(final_context.history[2].agent_name, "Janitor-Agent")
        self.assertIn("command", final_context.history[2].task_kwargs)
        
        # Verify Janitor task was staged for HITL
        janitor_result = json.loads(final_context.history[2].result)
        self.assertEqual(janitor_result["status"], "pending_hitl")
        
        # Check resolved status
        self.assertTrue(final_context.is_resolved)
            
        print("\n--- Multi-Step Integration Test Passed ---")
        print(f"Total Steps: {len(final_context.history)}")
        for step in final_context.history:
            print(f"- {step.agent_name}: {step.task} (Args: {step.task_kwargs})")

if __name__ == "__main__":
    unittest.main()
