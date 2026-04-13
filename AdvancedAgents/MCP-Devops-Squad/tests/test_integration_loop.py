import unittest
import json
import os
from src.agents.monitor import MonitorAgent
from src.orchestrator.lead_sre import LeadSRE
from src.agents.janitor import JanitorAgent

class TestSquadIntegration(unittest.TestCase):
    """Integration test for the full SRE Squad lifecycle."""
    
    def setUp(self):
        self.monitor = MonitorAgent()
        self.orchestrator = LeadSRE()
        self.janitor = JanitorAgent()
        self.resource_id = "integration-test-server"
        
        # Cleanup pending approvals
        if os.path.exists("config/pending_approvals.json"):
            with open("config/pending_approvals.json", "w") as f:
                json.dump([], f)

    def test_full_loop_cpu_spike(self):
        """Simulate a CPU spike and ensure the squad responds correctly."""
        
        # 1. MONITOR: Detect high CPU
        metrics = self.monitor.get_metrics(self.resource_id)
        self.assertTrue(metrics.cpu_percent > 80.0)
        
        # 2. LEAD-SRE: Analyze and decide to fix
        decision = self.orchestrator.analyze_situation(metrics)
        self.assertTrue(decision.action_required)
        
        # 3. JANITOR: Request execution (should trigger HITL for destructive fix)
        # Assuming the reasoning decides on a 'kill' command for a heavy process
        fix_command = "kill -9 1234" 
        result = self.janitor.request_execution(
            command=fix_command, 
            justification=decision.analysis, 
            resource_id=self.resource_id
        )
        
        # 4. VERIFY: Staged for manual approval
        self.assertEqual(result["status"], "pending_hitl")
        
        with open("config/pending_approvals.json", "r") as f:
            approvals = json.load(f)
            self.assertTrue(any(a["command"] == fix_command for a in approvals))
            
        print("\n--- Integration Test Passed ---")
        print(f"Decision: {decision.analysis}")
        print(f"Staged Fix: {fix_command}")

if __name__ == "__main__":
    unittest.main()
