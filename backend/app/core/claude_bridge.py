import asyncio
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import get_settings


class ClaudeBridge:
    """Interface to Claude Code CLI for agent orchestration."""

    def __init__(self):
        self.settings = get_settings()
        self.logs_dir = Path(self.settings.agent_logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

    async def invoke_agent(
        self,
        agent_name: str,
        prompt: str,
        project_id: str,
        working_dir: Optional[str] = None,
        context: Optional[dict] = None
    ) -> dict:
        """
        Invoke a Claude Code agent with the given prompt.

        Args:
            agent_name: Name of the agent (e.g., 'orchestrator-agent')
            prompt: The prompt to send to the agent
            project_id: Unique project identifier for tracking
            working_dir: Working directory for the agent
            context: Previous agent context for handover

        Returns:
            dict with status, output, and handover context
        """
        # Prepare the full prompt with context if provided
        full_prompt = prompt
        if context:
            context_str = json.dumps(context, indent=2)
            full_prompt = f"Previous agent context:\n```json\n{context_str}\n```\n\n{prompt}"

        # Build the claude command
        # Format: claude -p "prompt" --print --output-format json
        cmd = [
            self.settings.claude_cli_path,
            "-p", full_prompt,
            "--print",
            "--output-format", "json",
        ]

        if working_dir:
            cmd.extend(["--cwd", working_dir])

        # Log the invocation
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "project_id": project_id,
            "agent": agent_name,
            "prompt": prompt[:500],  # Truncate for logging
            "status": "started"
        }
        self._write_log(project_id, log_entry)

        try:
            # Run the agent
            result = await self._run_command(cmd, working_dir)

            # Update log with result
            log_entry.update({
                "status": "completed",
                "exit_code": result["exit_code"]
            })
            self._write_log(project_id, log_entry)

            return {
                "success": result["exit_code"] == 0,
                "output": result["stdout"],
                "error": result["stderr"],
                "agent": agent_name,
                "project_id": project_id
            }

        except Exception as e:
            log_entry.update({
                "status": "failed",
                "error": str(e)
            })
            self._write_log(project_id, log_entry)

            return {
                "success": False,
                "output": "",
                "error": str(e),
                "agent": agent_name,
                "project_id": project_id
            }

    async def _run_command(
        self,
        cmd: list[str],
        working_dir: Optional[str] = None
    ) -> dict:
        """Run a command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir
        )

        stdout, stderr = await process.communicate()

        return {
            "stdout": stdout.decode("utf-8"),
            "stderr": stderr.decode("utf-8"),
            "exit_code": process.returncode
        }

    def _write_log(self, project_id: str, entry: dict) -> None:
        """Write a log entry for the project."""
        log_file = self.logs_dir / f"{project_id}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_project_logs(self, project_id: str) -> list[dict]:
        """Get all log entries for a project."""
        log_file = self.logs_dir / f"{project_id}.jsonl"
        if not log_file.exists():
            return []

        logs = []
        with open(log_file) as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        return logs


# Singleton instance
_bridge: Optional[ClaudeBridge] = None


def get_claude_bridge() -> ClaudeBridge:
    global _bridge
    if _bridge is None:
        _bridge = ClaudeBridge()
    return _bridge
