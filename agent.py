#!/usr/bin/env python3
"""
Agent Helper CLI - Run common development tasks and utilities
Provides a convenient interface for git, grep, file analysis, and more
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, List


class AgentHelper:
    def __init__(self):
        self.repo_root = Path(__file__).parent

    def run_command(self, cmd: List[str], description: str = None) -> int:
        """Execute a shell command and return exit code"""
        if description:
            print(f"[*] {description}")
        print(f"$ {' '.join(cmd)}\n")
        try:
            result = subprocess.run(cmd, cwd=self.repo_root, timeout=300)
            return result.returncode
        except FileNotFoundError:
            print(f"[!] Command not found: {cmd[0]}")
            return 1
        except subprocess.TimeoutExpired:
            print("[!] Command timed out after 300 seconds")
            return 124
        except KeyboardInterrupt:
            print("\n[!] Interrupted")
            return 130

    def git_status(self) -> int:
        """Show git status"""
        return self.run_command(["git", "status"], "Git Status")

    def git_log(self, limit: int = 10) -> int:
        """Show git log with limit"""
        return self.run_command(
            ["git", "log", f"--oneline", f"-{limit}"],
            f"Git Log (last {limit} commits)"
        )

    def git_diff(self, staged: bool = False) -> int:
        """Show git diff"""
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        desc = "Git Diff (staged)" if staged else "Git Diff"
        return self.run_command(cmd, desc)

    def git_branch(self) -> int:
        """List git branches"""
        return self.run_command(["git", "branch", "-a"], "Git Branches")

    def git_add(self, files: str = ".") -> int:
        """Stage files for commit"""
        return self.run_command(["git", "add", files], f"Git Add ({files})")

    def git_commit(self, message: str) -> int:
        """Commit staged changes"""
        return self.run_command(["git", "commit", "-m", message], "Git Commit")

    def git_commit_multiline(self, *lines: str) -> int:
        """Commit staged changes with multi-line message"""
        if not lines:
            print("Usage: git-commit-multiline <line1> [line2] [line3] ...")
            return 1
        message = "\n".join(lines)
        return self.run_command(["git", "commit", "-m", message], "Git Commit (multiline)")

    def git_push(self, remote: str = "origin", branch: str = None) -> int:
        """Push commits to remote"""
        cmd = ["git", "push", remote]
        if branch:
            cmd.append(branch)
        desc = f"Git Push to {remote}" + (f" ({branch})" if branch else "")
        return self.run_command(cmd, desc)

    def git_rm(self, files: str = None, cached: bool = False) -> int:
        """Remove files from git tracking"""
        if not files:
            files = " ".join([
                "codex_clone/",
                "tests/",
                "codex_portable.py",
                "pyproject.toml",
                "run_tests.py",
                "run_tests.sh",
                "run_tests.bat"
            ])
        
        cmd = ["git", "rm"]
        if cached:
            cmd.append("--cached")
        cmd.append("-r")
        cmd.extend(files.split())
        
        desc = f"Git Remove ({files})" + (" (cached)" if cached else "")
        return self.run_command(cmd, desc)

    def commit_push(self, message: str, remote: str = "origin", branch: str = None) -> int:
        """Commit and push in one operation"""
        print(f"[*] Commit and Push")
        result = self.git_commit(message)
        if result != 0:
            print("[!] Commit failed, skipping push")
            return result
        return self.git_push(remote, branch)

    def grep_files(self, pattern: str, extensions: Optional[str] = None) -> int:
        """Search for pattern in files"""
        print(f"[*] Search for '{pattern}' in {extensions or 'all'} files\n")
        
        matches = 0
        pattern_ext = f".{extensions}" if extensions else ""
        
        for file_path in self.repo_root.rglob(f"*{pattern_ext}"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern in line:
                                rel_path = file_path.relative_to(self.repo_root)
                                print(f"{rel_path}:{line_num}: {line.rstrip()}")
                                matches += 1
                except (OSError, IOError):
                    pass
        
        if matches == 0:
            print(f"No matches found for '{pattern}'")
        else:
            print(f"\n{matches} matches found")
        
        return 0

    def count_lines(self, extension: Optional[str] = None) -> int:
        """Count lines in files"""
        total_lines = 0
        file_count = 0
        pattern = f"*.{extension}" if extension else "*"
        desc = f"Line count in .{extension} files" if extension else "Total line count in repository"
        
        print(f"[*] {desc}")
        print(f"Scanning for {pattern} files...\n")
        
        for file_path in self.repo_root.rglob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1
                        if lines > 0:
                            print(f"{lines:6d} {file_path.relative_to(self.repo_root)}")
                except (OSError, IOError):
                    pass
        
        print(f"\n{'-' * 50}")
        print(f"Total: {total_lines:6d} lines in {file_count} files")
        return 0

    def list_files(self, extension: Optional[str] = None, max_depth: int = 3) -> int:
        """List files by extension"""
        pattern = f"*.{extension}" if extension else "*"
        desc = f"Files with .{extension} extension (max depth: {max_depth})" if extension else f"All files (max depth: {max_depth})"
        
        print(f"[*] {desc}\n")
        
        files = []
        for file_path in self.repo_root.rglob(pattern):
            if file_path.is_file():
                depth = len(file_path.relative_to(self.repo_root).parts)
                if depth <= max_depth:
                    files.append(file_path.relative_to(self.repo_root))
        
        for file_path in sorted(files):
            print(file_path)
        
        print(f"\n{len(files)} files found")
        return 0

    def test(self) -> int:
        """Run tests"""
        return self.run_command(["python", "run_tests.py"], "Running Tests")

    def lint(self) -> int:
        """Run linting"""
        result = self.run_command(["pylint", "codex_clone/", "--disable=all", "--enable=E"], "Linting")
        if result != 0:
            print("[!] Note: pylint not installed. Install with: pip install pylint")
        return result

    def typecheck(self) -> int:
        """Run type checking"""
        result = self.run_command(["mypy", "codex_clone/"], "Type Checking")
        if result != 0:
            print("[!] Note: mypy not installed. Install with: pip install mypy")
        return result

    def count_lines_batch(self) -> int:
        """Count lines in .py files using Windows batch method"""
        if sys.platform != "win32":
            print("[!] This command is Windows-only")
            return 1
        
        cmd = 'for %f in (*.py) do @(for /f "tokens=3" %a in (\'find /c /v "" %f\') do @echo %a %f)'
        print("[*] Counting lines in Python files\n")
        return self.run_command(["cmd", "/c", cmd], "Windows batch line count")

    def show_help_message(self):
        """Display help for common tasks"""
        help_text = """
AGENT HELPER CLI - Common Development Tasks
=============================================

Usage: python agent.py <command> [options]

GIT COMMANDS
  git-status              Show current git status
  git-log [N]             Show last N commits (default: 10)
  git-diff                Show unstaged changes
  git-diff-staged         Show staged changes
  git-branch              List all branches
  git-add [files]         Stage files for commit (default: all)
  git-commit <message>    Commit staged changes
  git-commit-multiline <lines...> Commit with multi-line message
  git-push [remote] [branch] Push to remote (default: origin)
  commit-push <message> [remote] [branch] Commit and push in one operation
  git-rm [files] [--cached] Remove files from git (--cached keeps local files)

SEARCH & ANALYSIS
  grep <pattern>          Search pattern in all files
  grep <pattern> <ext>    Search pattern in files with extension
  count-lines [ext]       Count lines of code (optionally by extension)
  list-files [ext] [depth] List files (optionally filtered by extension)

TESTING & QUALITY
  test                    Run unit tests
  lint                    Run linter (requires pylint)
  typecheck               Run type checker (requires mypy)

UTILITIES
  count-lines-batch       Count .py files (Windows batch method)
  help                    Show this help message

EXAMPLES:
  python agent.py git-status
  python agent.py git-rm --cached
  python agent.py git-commit-multiline "Fix bug" "Add tests" "Update docs"
  python agent.py commit-push "Fixed issue X"
  python agent.py grep-files "def " py
  python agent.py count-lines py
  python agent.py list-files py 2
  python agent.py test
"""
        print(help_text)


def main():
    parser = argparse.ArgumentParser(
        description="Agent Helper CLI - Run common development tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run 'python agent.py help' for more information"
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="help",
        help="Command to execute"
    )

    parser.add_argument(
        "args",
        nargs="*",
        help="Additional arguments for the command"
    )

    parsed_args = parser.parse_args()
    agent = AgentHelper()

    command = parsed_args.command.lower().replace("-", "_")
    args = [arg.strip('"\'') for arg in parsed_args.args]

    commands = {
        "git_status": lambda: agent.git_status(),
        "git_log": lambda: agent.git_log(int(args[0]) if args else 10),
        "git_diff": lambda: agent.git_diff(),
        "git_diff_staged": lambda: agent.git_diff(staged=True),
        "git_branch": lambda: agent.git_branch(),
        "git_add": lambda: agent.git_add(args[0] if args else "."),
        "git_commit": lambda: agent.git_commit(args[0]) if args else print("Usage: git-commit <message>"),
        "git_commit_multiline": lambda: agent.git_commit_multiline(*args) if args else print("Usage: git-commit-multiline <line1> [line2] ..."),
        "git_push": lambda: agent.git_push(args[0] if args else "origin", args[1] if len(args) > 1 else None),
        "commit_push": lambda: agent.commit_push(args[0], args[1] if len(args) > 1 else "origin", args[2] if len(args) > 2 else None) if args else print("Usage: commit-push <message> [remote] [branch]"),
        "git_rm": lambda: agent.git_rm(args[0] if args else None, "--cached" in args or "-c" in args),
        "grep_files": lambda: agent.grep_files(args[0], args[1] if len(args) > 1 else None) if args else print("Usage: grep-files <pattern> [extension]"),
        "count_lines": lambda: agent.count_lines(args[0] if args else None),
        "list_files": lambda: agent.list_files(args[0] if args else None, int(args[1]) if len(args) > 1 else 3),
        "test": lambda: agent.test(),
        "lint": lambda: agent.lint(),
        "typecheck": lambda: agent.typecheck(),
        "count_lines_batch": lambda: agent.count_lines_batch(),
        "help": lambda: agent.show_help_message(),
    }

    if command in commands:
        exit_code = commands[command]()
        sys.exit(exit_code if isinstance(exit_code, int) else 0)
    else:
        print(f"[ERROR] Unknown command: {parsed_args.command}")
        print("Run 'python agent.py help' for available commands")
        sys.exit(1)


if __name__ == "__main__":
    main()
