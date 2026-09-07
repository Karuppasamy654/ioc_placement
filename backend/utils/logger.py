import sys
import time
import datetime
from typing import Optional, Any, Dict

# Ensure Windows console supports UTF-8 characters gracefully
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def print_banner(title: str, subtitle: str = ""):
    print(f"\n============================================================", flush=True)
    print(f"[PIPELINE] {title.upper()}", flush=True)
    if subtitle:
        print(f"   {subtitle}", flush=True)
    print(f"============================================================\n", flush=True)

def print_section(section_name: str, emoji: str = "AGENT"):
    print(f"\n------------------------------------------------------------", flush=True)
    print(f"[{emoji}] {section_name.upper()}", flush=True)
    print(f"------------------------------------------------------------", flush=True)

def print_state_transition(from_state: str, to_state: str, state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[STATE TRANSITION] {from_state.upper()} -> {to_state.upper()}"
    print(f"[{now_str}] {msg}", flush=True)
    if state is not None:
        state.add_event(agent_name="State Graph", message=msg, status="INFO")


def log_agent_start(agent_name: str, input_summary: str, state=None) -> float:
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[AGENT START] {agent_name}\n[INPUT] {input_summary}"
    print(f"[{now_str}] {msg}", flush=True)
    if state is not None:
        state.add_event(agent_name=agent_name, message=f"Started: {input_summary}", status="STARTED")
    return time.time()

def log_agent_action(agent_name: str, action_desc: str, state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[AGENT ACTION] {action_desc}"
    print(f"[{now_str}] {msg}", flush=True)
    if state is not None:
        state.add_event(agent_name=agent_name, message=action_desc, status="INFO")

def log_agent_end(agent_name: str, result_summary: str, start_time: float, state=None):
    duration = round(time.time() - start_time, 2)
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[AGENT RESULT] {result_summary}\n[AGENT END] {agent_name} (Duration: {duration}s)"
    print(f"[{now_str}] {msg}\n", flush=True)
    if state is not None:
        state.add_event(agent_name=agent_name, message=f"Completed in {duration}s: {result_summary}", status="COMPLETED")

def log_tool_start(tool_name: str, input_summary: str, state=None) -> float:
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[TOOL START] {tool_name}\n[TOOL INPUT] {input_summary}"
    print(f"[{now_str}] {msg}", flush=True)
    if state is not None:
        state.add_event(agent_name=tool_name, message=f"Input: {input_summary}", status="STARTED")
    return time.time()

def log_tool_process(tool_name: str, process_desc: str, state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[TOOL PROCESS] {process_desc}"
    print(f"[{now_str}] {msg}", flush=True)
    if state is not None:
        state.add_event(agent_name=tool_name, message=process_desc, status="INFO")

def log_tool_result(tool_name: str, result_summary: str, start_time: float, state=None):
    duration = round(time.time() - start_time, 2)
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[TOOL RESULT] {result_summary}\n[TOOL END] {tool_name} (Duration: {duration}s)"
    print(f"[{now_str}] {msg}\n", flush=True)
    if state is not None:
        state.add_event(agent_name=tool_name, message=f"Completed in {duration}s: {result_summary}", status="COMPLETED")

def log_gemini_request(model_name: str, purpose: str, state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[GEMINI REQUEST]\nModel: {model_name}\nPurpose: {purpose}"
    print(f"[{now_str}] {msg}", flush=True)
    if state is not None:
        state.add_event(agent_name="Gemini Service", message=f"Request to {model_name} for {purpose}", status="INFO")

def log_gemini_response(status: str, output_size: int, duration: float, state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[GEMINI RESPONSE]\nStatus: {status}\nOutput Size: {output_size} characters\nDuration: {round(duration, 2)}s"
    print(f"[{now_str}] {msg}\n", flush=True)
    if state is not None:
        state.add_event(agent_name="Gemini Service", message=f"Response {status} ({output_size} chars in {round(duration, 2)}s)", status="INFO")

def log_gemini_error(error_msg: str, state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = f"[GEMINI ERROR] {error_msg}"
    print(f"[{now_str}] {msg}\n", flush=True)
    if state is not None:
        state.add_event(agent_name="Gemini Service", message=f"Error: {error_msg}", status="FAILED")

def log_memory_op(op_type: str, message: str, result_summary: str = "", state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"------------------------------------------------------------", flush=True)
    print(f"🧠 MEMORY SYSTEM", flush=True)
    print(f"------------------------------------------------------------", flush=True)
    print(f"[{now_str}] [{op_type.upper()}] {message}", flush=True)
    if result_summary:
        print(f"[{now_str}] [MEMORY RESULT] {result_summary}", flush=True)
    print(f"[MEMORY COMPLETE]\n", flush=True)

    if state is not None:
        state.add_event(agent_name="Memory System", message=f"{op_type}: {message} | {result_summary}", status="INFO")

def log_error(agent_or_tool: str, error_type: str, error_msg: str, recovery_msg: str = "", state=None):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}] [ERROR] Location: {agent_or_tool}", flush=True)
    print(f"[{now_str}] [ERROR TYPE] {error_type}", flush=True)
    print(f"[{now_str}] [ERROR MSG] {error_msg}", flush=True)
    if recovery_msg:
        print(f"[{now_str}] [RECOVERY] {recovery_msg}", flush=True)
    print(flush=True)

    if state is not None:
        state.add_event(agent_name=agent_or_tool, message=f"ERROR ({error_type}): {error_msg}", status="FAILED")

def log_event(agent_name: str, message: str, status: str = "INFO", state=None):
    """
    General purpose logging fallback maintaining legacy interface compatibility.
    """
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}] [{agent_name.upper()}] ({status}) - {message}", flush=True)
    if state is not None:
        state.add_event(agent_name=agent_name, message=message, status=status)
