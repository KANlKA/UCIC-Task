#!/usr/bin/env python3

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8008
FILENAME = "index.html"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(FILENAME):
    print(f"Can't find {FILENAME} in this folder.")
    print(f"Put serve.py in the same folder as {FILENAME}, then run it again.")
    sys.exit(1)


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    port = PORT
    for candidate in range(PORT, PORT + 10):
        try:
            httpd = socketserver.TCPServer(("", candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    else:
        print(f"Ports {PORT}-{PORT + 9} are all in use. Close whatever is using them and retry.")
        sys.exit(1)

    url = f"http://localhost:{port}/{FILENAME}"
 
    print("Opening it in your browser now. Press Ctrl+C here to stop.")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
