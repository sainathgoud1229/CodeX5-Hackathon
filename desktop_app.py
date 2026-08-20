"""
DocuSense AI — Desktop App Launcher
Wraps the Streamlit app in a native desktop window using pywebview.
No modifications to app.py or any other source files.
"""

import subprocess
import threading
import time
import sys
import os
import socket
import webbrowser

# Try to use pywebview for a native window, fallback to browser
try:
    import webview
    USE_WEBVIEW = True
except ImportError:
    USE_WEBVIEW = False

PORT = 8502
APP_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def find_free_port():
    """Find a free port to run the Streamlit server on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def wait_for_server(port, timeout=30):
    """Wait until Streamlit server is ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("localhost", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def start_streamlit(port):
    """Launch Streamlit as a background subprocess."""
    cmd = [
        sys.executable, "-m", "streamlit", "run", APP_SCRIPT,
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.runOnSave", "false",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(APP_SCRIPT)
    )
    return process


def main():
    global PORT
    PORT = find_free_port()
    url = f"http://localhost:{PORT}"

    print(f"[DocuSense AI] Starting server on {url} ...")

    # Start Streamlit in background
    streamlit_proc = start_streamlit(PORT)

    # Wait for it to be ready
    if not wait_for_server(PORT, timeout=40):
        print("[DocuSense AI] ERROR: Server did not start in time.")
        streamlit_proc.terminate()
        sys.exit(1)

    print(f"[DocuSense AI] Server ready at {url}")

    if USE_WEBVIEW:
        # Launch in native desktop window (no browser bar, no tabs)
        try:
            webview.create_window(
                title="DocuSense AI — Contract & Policy Analyzer",
                url=url,
                width=1280,
                height=860,
                resizable=True,
                min_size=(900, 600),
            )
            webview.start()
        except Exception as e:
            print(f"[DocuSense AI] pywebview error: {e}. Opening in browser.")
            webbrowser.open(url)
            input("Press Enter to close the server...")
    else:
        # Fallback: open in default browser
        print("[DocuSense AI] pywebview not found — opening in browser.")
        print("[DocuSense AI] Install pywebview for a native window: pip install pywebview")
        webbrowser.open(url)
        print("[DocuSense AI] App is running. Close this window to stop the server.")
        try:
            streamlit_proc.wait()
        except KeyboardInterrupt:
            pass

    # Clean up
    streamlit_proc.terminate()
    print("[DocuSense AI] Server stopped.")


if __name__ == "__main__":
    main()
