"""
Gemini Bridge Script for Claude Agent Skills.
Wraps the Gemini CLI to provide a JSON-based interface for Claude.
"""

import json
import ctypes
import os
import sys
import queue
import subprocess
import threading
import time
import shutil
import argparse
import signal
from ctypes import wintypes
from pathlib import Path
from typing import Generator, List, Optional


class _WindowsIoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in [
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    ]]


class _WindowsBasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _WindowsExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _WindowsBasicLimits), ("IoInfo", _WindowsIoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _WindowsJob:
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9

    def __init__(self) -> None:
        self.handle = None
        if os.name != "nt":
            return
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel32.CreateJobObjectW(None, None)
        if not handle:
            return
        limits = _WindowsExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = self.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not kernel32.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            kernel32.CloseHandle(handle)
            return
        self.handle = handle

    def assign(self, process: subprocess.Popen) -> bool:
        if self.handle is None:
            return False
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        if not kernel32.AssignProcessToJobObject(self.handle, wintypes.HANDLE(process._handle)):
            self.close()
            return False
        return True

    def close(self) -> None:
        if self.handle is not None:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle(self.handle)
            self.handle = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def _get_windows_npm_paths() -> List[Path]:
    """Return candidate directories for npm global installs on Windows."""
    if os.name != "nt":
        return []
    paths: List[Path] = []
    env = os.environ
    if prefix := env.get("NPM_CONFIG_PREFIX") or env.get("npm_config_prefix"):
        paths.append(Path(prefix))
    if appdata := env.get("APPDATA"):
        paths.append(Path(appdata) / "npm")
    if localappdata := env.get("LOCALAPPDATA"):
        paths.append(Path(localappdata) / "npm")
    if programfiles := env.get("ProgramFiles"):
        paths.append(Path(programfiles) / "nodejs")
    return paths


def _augment_path_env(env: dict) -> None:
    """Prepend npm global directories to PATH if missing."""
    if os.name != "nt":
        return
    path_key = next((k for k in env if k.upper() == "PATH"), "PATH")
    path_entries = [p for p in env.get(path_key, "").split(os.pathsep) if p]
    lower_set = {p.lower() for p in path_entries}
    for candidate in _get_windows_npm_paths():
        if candidate.is_dir() and str(candidate).lower() not in lower_set:
            path_entries.insert(0, str(candidate))
            lower_set.add(str(candidate).lower())
    env[path_key] = os.pathsep.join(path_entries)


def _resolve_executable(name: str, env: dict) -> str:
    """Resolve executable path, checking npm directories for .cmd/.bat on Windows."""
    if os.path.isabs(name) or os.sep in name or (os.altsep and os.altsep in name):
        return name
    path_key = next((k for k in env if k.upper() == "PATH"), "PATH")
    path_val = env.get(path_key)
    win_exts = {".exe", ".cmd", ".bat", ".com"}
    if resolved := shutil.which(name, path=path_val):
        if os.name == "nt":
            suffix = Path(resolved).suffix.lower()
            if not suffix:
                resolved_dir = str(Path(resolved).parent)
                for ext in (".cmd", ".bat", ".exe", ".com"):
                    candidate = Path(resolved_dir) / f"{name}{ext}"
                    if candidate.is_file():
                        return str(candidate)
            elif suffix not in win_exts:
                return resolved
        return resolved
    if os.name == "nt":
        for base in _get_windows_npm_paths():
            for ext in (".cmd", ".bat", ".exe", ".com"):
                candidate = base / f"{name}{ext}"
                if candidate.is_file():
                    return str(candidate)
    return name


def run_shell_command(cmd: List[str], cwd: Optional[str] = None, timeout: int = 600) -> Generator[str, None, None]:
    """Execute a command and stream its output line-by-line."""
    env = os.environ.copy()
    _augment_path_env(env)

    popen_cmd = cmd.copy()
    exe_path = _resolve_executable(cmd[0], env)
    popen_cmd[0] = exe_path

    # Windows .cmd/.bat files need cmd.exe wrapper (avoid shell=True for security)
    if os.name == "nt" and Path(exe_path).suffix.lower() in {".cmd", ".bat"}:
        # Escape shell metacharacters for cmd.exe
        def _cmd_quote(arg: str) -> str:
            if not arg:
                return '""'
            # For Windows batch files, % and ^ must be escaped before quoting
            arg = arg.replace('%', '%%')
            arg = arg.replace('^', '^^')
            if any(c in arg for c in '&|<>()^" \t'):
                # To safely escape " inside "...", close quote, escape ", reopen
                escaped = arg.replace('"', '"^""')
                return f'"{escaped}"'
            return arg
        cmdline = " ".join(_cmd_quote(a) for a in popen_cmd)
        comspec = env.get("COMSPEC", "cmd.exe")
        # Use a single string to avoid subprocess list escaping on Windows
        popen_cmd = f'"{comspec}" /d /s /c "{cmdline}"'

    windows_job = _WindowsJob()
    process = subprocess.Popen(
        popen_cmd,
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',
        errors='replace',
        cwd=cwd,
        env=env,
        start_new_session=os.name != "nt",
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0,
    )
    windows_job.assign(process)

    output_queue: "queue.Queue[Optional[str]]" = queue.Queue(maxsize=1024)
    stop_event = threading.Event()
    completed_event = threading.Event()
    GRACEFUL_SHUTDOWN_DELAY = 0.3

    def terminate_process_tree() -> None:
        if os.name == "nt":
            if windows_job.handle is not None:
                windows_job.close()
                process.wait()
                return
            if process.poll() is not None:
                return
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=2)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
        if process.poll() is None:
            process.kill()
        process.wait()

    def enqueue(value: Optional[str]) -> bool:
        while not stop_event.is_set():
            try:
                output_queue.put(value, timeout=0.1)
                return True
            except queue.Full:
                continue
        return False

    def is_turn_completed(line: str) -> bool:
        try:
            data = json.loads(line)
            return data.get("type") == "turn.completed"
        except (json.JSONDecodeError, AttributeError, TypeError):
            return False

    def read_output() -> None:
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                stripped = line.strip()
                if not enqueue(stripped):
                    break
                if is_turn_completed(stripped):
                    completed_event.set()
                    time.sleep(GRACEFUL_SHUTDOWN_DELAY)
                    terminate_process_tree()
                    break
            process.stdout.close()
        enqueue(None)

    thread = threading.Thread(target=read_output, daemon=True)
    thread.start()
    deadline = time.monotonic() + timeout

    timed_out = False
    while True:
        if time.monotonic() >= deadline:
            timed_out = True
            break
        try:
            line = output_queue.get(timeout=min(0.1, max(0.001, deadline - time.monotonic())))
            if line is None:
                break
            yield line
        except queue.Empty:
            if process.poll() is not None and not thread.is_alive():
                break

    if timed_out:
        stop_event.set()
        terminate_process_tree()
        thread.join(timeout=1)
        yield "__HELLOAGENTS_TIMEOUT__"
        return

    remaining = deadline - time.monotonic()
    if process.poll() is None:
        try:
            process.wait(timeout=max(0.001, remaining))
        except subprocess.TimeoutExpired:
            stop_event.set()
            terminate_process_tree()
            thread.join(timeout=1)
            yield "__HELLOAGENTS_TIMEOUT__"
            return
    thread.join(timeout=1)

    while not output_queue.empty():
        try:
            line = output_queue.get_nowait()
            if line is not None:
                yield line
        except queue.Empty:
            break

    if process.returncode and not completed_event.is_set():
        yield f"__HELLOAGENTS_EXIT_CODE__={process.returncode}"
    windows_job.close()


def build_command(args: argparse.Namespace) -> List[str]:
    cmd = ["gemini", "--prompt", args.PROMPT, "-o", "stream-json"]
    if args.sandbox:
        cmd.extend(["--sandbox", "--approval-mode", "plan"])
    if args.model.strip():
        cmd.extend(["--model", args.model.strip()])
    if args.SESSION_ID:
        cmd.extend(["--resume", args.SESSION_ID])
    return cmd


def configure_windows_stdio() -> None:
    """Configure stdout/stderr to use UTF-8 encoding on Windows."""
    if os.name != "nt":
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def main():
    configure_windows_stdio()
    parser = argparse.ArgumentParser(description="Gemini Bridge")
    parser.add_argument("--PROMPT", required=True, help="Instruction for the task to send to gemini.")
    parser.add_argument("--cd", required=True, type=Path, help="Set the workspace root for gemini before executing the task.")
    parser.add_argument("--sandbox", action=argparse.BooleanOptionalAction, default=True, help="Run in sandbox mode. Defaults to `True`; use --no-sandbox only with explicit authorization.")
    parser.add_argument("--SESSION_ID", default="", help="Resume the specified session of the gemini. Defaults to empty string, start a new session.")
    parser.add_argument("--return-all-messages", action="store_true", help="Return all messages (e.g. reasoning, tool calls, etc.) from the gemini session. Set to `False` by default, only the agent's final reply message is returned.")
    parser.add_argument("--model", default="", help="Optional model passthrough to Gemini CLI. No automatic model switching is applied.")
    parser.add_argument("--timeout", type=int, default=600, help="Maximum runtime in seconds. Defaults to 600.")

    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    cd: Path = args.cd
    if not cd.exists():
        result = {
            "success": False,
            "error": f"The workspace root directory `{cd.absolute()}` does not exist. Please check the path and try again."
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    PROMPT = args.PROMPT

    cmd = build_command(args)

    all_messages = []
    agent_messages = ""
    success = True
    err_message = ""
    thread_id = None

    for line in run_shell_command(cmd, cwd=str(cd.absolute()), timeout=args.timeout):
        if line == "__HELLOAGENTS_TIMEOUT__":
            success = False
            err_message += f"\n\n[gemini timeout] exceeded {args.timeout} seconds"
            break
        if line.startswith("__HELLOAGENTS_EXIT_CODE__="):
            success = False
            err_message += "\n\n[gemini error] process " + line.removeprefix("__HELLOAGENTS_")
            break
        try:
            line_dict = json.loads(line.strip())
            all_messages.append(line_dict)
            item_type = line_dict.get("type", "")
            item_role = line_dict.get("role", "")
            if item_type == "message" and item_role == "assistant":
                if (
                    "The --prompt (-p) flag has been deprecated and will be removed in a future version. Please use a positional argument for your prompt. See gemini --help for more information.\n"
                    in line_dict.get("content", "")
                ):
                    continue
                agent_messages = agent_messages + line_dict.get("content", "")
            if line_dict.get("session_id") is not None:
                thread_id = line_dict.get("session_id")
            event_type = str(line_dict.get("type", "")).lower()
            if "error" in event_type or "fail" in event_type or line_dict.get("error"):
                success = False
                err_message += "\n\n[gemini error] " + str(
                    line_dict.get("error") or line_dict.get("message") or line_dict
                )

        except json.JSONDecodeError:
            err_message += "\n\n[json decode error] " + line
            continue

        except Exception as error:
            err_message += "\n\n[unexpected error] " + f"Unexpected error: {error}. Line: {line!r}"
            success = False
            break
    
    result = {}
    
    if thread_id is None:
        success = False
        err_message = "Failed to get `SESSION_ID` from the gemini session. \n\n" + err_message
    else:
        result["SESSION_ID"] = thread_id

    if success and len(agent_messages) == 0:
        success = False
        err_message = (
            "Failed to retrieve `agent_messages` data from the Gemini session. This might be due to Gemini performing a tool call. You can continue using the `SESSION_ID` to proceed with the conversation. \n\n "
            + err_message
        )
    
    
    if success:
        result["agent_messages"] = agent_messages
    else:
        result["error"] = err_message
        
    result["success"] = success

    if args.return_all_messages:
        result["all_messages"] = all_messages

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
