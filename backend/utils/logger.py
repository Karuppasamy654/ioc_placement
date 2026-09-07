import sys
import datetime

def log_event(agent_name: str, message: str, status: str = "INFO", state=None):
    """
    Logs structured event to terminal stdout and appends to session state if available.
    """
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Print formatted block to terminal stdout for demo
    if agent_name.upper() == "ORCHESTRATOR" and ("started" in message.lower() or "completed" in message.lower()):
        print(f"\n====================================================", flush=True)
        print(f"[{now_str}] [{agent_name.upper()}] - [{status}]", flush=True)
        print(f"{message}", flush=True)
        print(f"====================================================\n", flush=True)
    else:
        print(f"[{now_str}] [{agent_name.upper()}] ({status})", flush=True)
        print(f"{message}\n", flush=True)
        
    if state is not None:
        state.add_event(agent_name=agent_name, message=message, status=status)
