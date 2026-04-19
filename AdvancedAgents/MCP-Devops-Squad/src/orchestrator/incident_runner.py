import json
from src.utils.logger import setup_logger
from src.agents.monitor import MonitorAgent
from src.agents.debugger import DebuggerAgent
from src.agents.janitor import JanitorAgent
from src.agents.sargent import SargentAgent
from src.orchestrator.lead_sre import LeadSRE, IncidentContext, ActionHistory

class IncidentRunner:
    """Executes the multi-step orchestration loop for an incident."""
    
    def __init__(self):
        self.logger = setup_logger("Incident-Runner")
        self.lead_sre = LeadSRE()
        self.monitor = MonitorAgent()
        self.debugger = DebuggerAgent()
        self.janitor = JanitorAgent()
        self.sargent = SargentAgent()
        self.max_iterations = 5

    def run(self, resource_id: str) -> IncidentContext:
        """Run the incident investigation and remediation loop."""
        self.logger.info("starting_incident_run", resource_id=resource_id)
        
        # 1. Fetch initial trigger
        metrics = self.monitor.get_metrics(resource_id)
        context = IncidentContext(initial_trigger=metrics)
        
        # 2. Execution Loop
        for i in range(self.max_iterations):
            self.logger.info("orchestration_loop_iteration", iteration=i+1)
            
            # Get decision from Lead-SRE
            decision = self.lead_sre.analyze_situation(context)
            
            if not decision.action_required:
                self.logger.info("incident_resolved_or_no_action", analysis=decision.analysis)
                context.is_resolved = True
                break
                
            agent_name = decision.target_agent
            task = decision.task_description
            self.logger.info("delegating_task", agent=agent_name, task=task)
            
            result_str = self._dispatch_to_agent(agent_name, task, resource_id)
            
            # Record history
            context.history.append(ActionHistory(
                agent_name=agent_name,
                task=task,
                result=result_str
            ))
            
        return context

    def _dispatch_to_agent(self, agent_name: str, task: str, resource_id: str) -> str:
        """Simple dispatcher to translate Lead-SRE tasks into agent method calls."""
        try:
            if agent_name == "Debugger-Agent":
                # Basic heuristic: if it mentions 'code' or 'repo', analyze code. Else logs.
                if "code" in task.lower() or "repo" in task.lower():
                    res = self.debugger.analyze_code("org/repo", "src/main.py")
                else:
                    res = self.debugger.analyze_logs(f"/var/log/{resource_id}.log")
                return json.dumps(res)
                
            elif agent_name == "Sargent-Agent":
                # Heuristic: 'image' vs 'path'
                scan_type = "image" if "image" in task.lower() else "path"
                res = self.sargent.run_security_scan(f"{resource_id}-image", scan_type=scan_type)
                return res.model_dump_json()
                
            elif agent_name == "Janitor-Agent":
                # We assume the task description contains the command, or we use a default based on the task
                command = "systemctl restart app"
                if "kill" in task.lower():
                    command = "kill -9 1234"
                elif "restart" in task.lower():
                    command = "systemctl restart app"
                elif "rm" in task.lower() or "cleanup" in task.lower():
                    command = "rm -rf /tmp/stale-logs"
                
                res = self.janitor.request_execution(command, justification=task, resource_id=resource_id)
                return json.dumps(res)
                
            elif agent_name == "Monitor-Agent":
                res = self.monitor.get_metrics(resource_id)
                return res.model_dump_json()
                
            else:
                return f"Error: Unknown agent {agent_name}"
                
        except Exception as e:
            self.logger.error("agent_execution_failed", agent=agent_name, error=str(e))
            return f"Execution failed: {str(e)}"

if __name__ == "__main__":
    runner = IncidentRunner()
    final_context = runner.run("server-99")
    print("\n--- Final Incident Context ---")
    print(final_context.model_dump_json(indent=2))
