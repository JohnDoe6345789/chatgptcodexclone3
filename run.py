#!/usr/bin/env python3
"""
Bootstrap installer for Codex Portable.
Handles dependency installation with GUI (tkinter or ncurses fallback).
Run: python run.py
"""

import sys
import subprocess
from pathlib import Path


REQUIRED_PACKAGES = {
    "PyQt6": "PyQt6>=6.4.0",
    "yaml": "PyYAML>=6.0",
}

OPTIONAL_PACKAGES = {
    "huggingface_hub": "huggingface_hub>=0.16.0",
    "llama_cpp": "llama-cpp-python>=0.2.0",
}


def check_dependencies():
    """Return dict of missing required packages."""
    missing = {}
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(module_name)
        except ImportError:
            missing[module_name] = pip_name
    return missing


def check_optional_dependencies():
    """Return dict of missing optional packages."""
    missing = {}
    for module_name, pip_name in OPTIONAL_PACKAGES.items():
        try:
            __import__(module_name)
        except ImportError:
            missing[module_name] = pip_name
    return missing


def try_tkinter_gui():
    """Try to show tkinter GUI for installation. Returns True/False or None if unavailable."""
    try:
        import tkinter as tk
        from tkinter import scrolledtext, messagebox
        
        missing_required = check_dependencies()
        
        if not missing_required:
            return True
        
        result = {"proceed": False}
        
        root = tk.Tk()
        root.title("Codex Portable - Setup Required")
        root.geometry("600x400")
        
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(frame, text="Missing Dependencies", font=("Arial", 14, "bold"))
        title.pack(pady=(0, 10))
        
        info = tk.Label(
            frame,
            text="The following Python packages are required:\n",
            justify=tk.LEFT
        )
        info.pack(anchor=tk.W)
        
        packages_text = scrolledtext.ScrolledText(frame, height=6, width=70, state=tk.DISABLED)
        packages_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        packages_text.config(state=tk.NORMAL)
        for pkg in missing_required.values():
            packages_text.insert(tk.END, f"  • {pkg}\n")
        packages_text.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        def on_install():
            result["proceed"] = True
            root.destroy()
        
        def on_exit():
            result["proceed"] = False
            root.destroy()
        
        install_btn = tk.Button(
            button_frame,
            text="Install Now",
            command=on_install,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        install_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            command=on_exit,
            bg="#f44336",
            fg="white",
            padx=20,
            pady=10
        )
        exit_btn.pack(side=tk.LEFT, padx=5)
        
        root.mainloop()
        
        if result["proceed"]:
            return _do_tkinter_install(missing_required)
        return False
    
    except ImportError:
        return None


def _do_tkinter_install(packages_dict):
    """Install packages via pip and show result."""
    try:
        packages = list(packages_dict.values())
        print(f"\nInstalling: {', '.join(packages)}\n")
        
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + packages,
            stdout=subprocess.PIPE
        )
        
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Success", "Dependencies installed successfully!\n\nLaunching application...")
        root.destroy()
        return True
    
    except subprocess.CalledProcessError as e:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Installation failed: {e}")
        root.destroy()
        return False


def try_ncurses_installer():
    """Fallback ncurses-based installer for Linux. Returns True/False or None if unavailable."""
    try:
        import curses
        
        missing_required = check_dependencies()
        
        if not missing_required:
            return True
        
        def ncurses_main(stdscr):
            curses.curs_set(0)
            stdscr.nodelay(False)
            
            while True:
                stdscr.clear()
                h, w = stdscr.getmaxyx()
                
                stdscr.addstr(0, 0, "=" * w)
                stdscr.addstr(1, (w - 25) // 2, "Codex Portable - Setup")
                stdscr.addstr(2, 0, "=" * w)
                
                stdscr.addstr(4, 2, "Missing required packages:")
                
                for i, pkg in enumerate(missing_required.values(), 1):
                    stdscr.addstr(5 + i, 4, f"• {pkg}")
                
                stdscr.addstr(h - 4, 2, "Press [I] to install, [Q] to quit")
                stdscr.addstr(h - 2, 0, "=" * w)
                stdscr.refresh()
                
                ch = stdscr.getch()
                if ch in (ord('i'), ord('I')):
                    curses.endwin()
                    packages = list(missing_required.values())
                    print(f"\nInstalling: {', '.join(packages)}\n")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install"] + packages
                    )
                    print("\n✓ Installation complete!")
                    return True
                
                elif ch in (ord('q'), ord('Q')):
                    return False
        
        curses.wrapper(ncurses_main)
        return True
    
    except ImportError:
        return None


def install_via_pip():
    """Non-interactive pip installation for CI/headless environments."""
    missing_required = check_dependencies()
    
    if not missing_required:
        return True
    
    print("Missing dependencies detected:")
    for pkg in missing_required.values():
        print(f"  • {pkg}")
    
    print("\nInstalling via pip...")
    
    try:
        packages = list(missing_required.values())
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + packages
        )
        print("✓ Installation complete!\n")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"✗ Installation failed: {e}")
        return False


def launch_application():
    """Import and launch the main application."""
    from codex_clone.logging_utils import setup_logging
    import logging
    
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Dependencies satisfied, launching Codex Portable...")
    
    import codex_portable
    codex_portable.main()


def main():
    """Main entry point."""
    missing = check_dependencies()
    
    if not missing:
        print("✓ All dependencies installed, launching...")
        launch_application()
        return 0
    
    print("Dependencies missing. Attempting installation...\n")
    
    installer_succeeded = None
    
    if sys.platform in ("win32", "darwin"):
        installer_succeeded = try_tkinter_gui()
        if installer_succeeded is None:
            print("Tkinter GUI not available, falling back to command-line installation.\n")
    elif sys.platform == "linux":
        print("Detected Linux environment.\n")
        installer_succeeded = try_ncurses_installer()
        if installer_succeeded is None:
            print("ncurses installation not available, falling back to command-line.\n")
    else:
        print(f"Unknown platform: {sys.platform}, using command-line installation.\n")
    
    if installer_succeeded is None or installer_succeeded is False:
        if not install_via_pip():
            return 1
    
    missing_after = check_dependencies()
    if missing_after:
        print("✗ Some dependencies still missing after installation.")
        return 1
    
    print("\n✓ All dependencies satisfied!")
    launch_application()
    return 0


if __name__ == "__main__":
    sys.exit(main())
