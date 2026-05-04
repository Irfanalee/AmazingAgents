import json
import os
import sys
from src.agents.janitor import JanitorAgent
from src.utils.logger import setup_logger

def main():
    logger = setup_logger("HITL-CLI")
    janitor = JanitorAgent()
    approval_file = janitor.approval_file

    if not os.path.exists(approval_file):
        print(f"No approval file found at {approval_file}")
        return

    with open(approval_file, "r") as f:
        try:
            pending_requests = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding {approval_file}")
            return

    if not pending_requests:
        print("No pending commands to review.")
        return

    print(f"\n--- HITL Approval Interface ---")
    print(f"Found {len(pending_requests)} pending command(s).\n")

    remaining_requests = []
    
    for i, req in enumerate(pending_requests):
        command = req.get("command")
        justification = req.get("justification")
        resource_id = req.get("resource_id")

        print(f"[{i+1}/{len(pending_requests)}] PENDING COMMAND")
        print(f"  Resource: {resource_id}")
        print(f"  Command:  {command}")
        print(f"  Reason:   {justification}")
        
        while True:
            choice = input("\nAction ([A]pprove, [R]eject, [S]kip, [Q]uit): ").strip().upper()
            
            if choice == 'A':
                print(f"Executing: {command}...")
                result = janitor.execute_approved_command(command)
                print(f"Result: {json.dumps(result, indent=2)}")
                break
            elif choice == 'R':
                print("Command rejected.")
                break
            elif choice == 'S':
                print("Skipping for now.")
                remaining_requests.append(req)
                break
            elif choice == 'Q':
                print("Quitting. Remaining commands will stay in queue.")
                remaining_requests.extend(pending_requests[i:])
                save_remaining(approval_file, remaining_requests)
                return
            else:
                print("Invalid choice. Please use A, R, S, or Q.")

    save_remaining(approval_file, remaining_requests)
    print("\nReview session complete.")

def save_remaining(file_path, requests):
    with open(file_path, "w") as f:
        json.dump(requests, f, indent=2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)
