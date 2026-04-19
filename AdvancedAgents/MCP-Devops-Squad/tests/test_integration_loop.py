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
        # Step 2: Lead-SRE should have delegated to Debugger-Agent (in mock mode)
        # Step 3: Lead-SRE should have delegated to Janitor-Agent (in mock mode)
        # Step 4: Final iteration should mark as resolved
        
        self.assertTrue(len(final_context.history) >= 2, f"History too short: {len(final_context.history)}")
        
        # Check first action was Debugger
        self.assertEqual(final_context.history[0].agent_name, "Debugger-Agent")
        
        # Check second action was Janitor
        self.assertEqual(final_context.history[1].agent_name, "Janitor-Agent")
        
        # Verify Janitor task was staged for HITL (since mock 'kill' is sensitive)
        janitor_result = json.loads(final_context.history[1].result)
        self.assertEqual(janitor_result["status"], "pending_hitl")
        
        # Check resolved status
        # Note: in my mock, it might take 3 calls to be 'not action_required'
        self.assertTrue(final_context.is_resolved)
            
        print("\n--- Multi-Step Integration Test Passed ---")
        print(f"Total Steps: {len(final_context.history)}")
        for step in final_context.history:
            print(f"- {step.agent_name}: {step.task}")

if __name__ == "__main__":
    unittest.main()
