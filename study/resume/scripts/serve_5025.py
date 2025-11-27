import http.server
import socketserver
import os
import sys

PORT = 5025
DIRECTORY = os.path.join('study', 'resume', 'web_build')

# Ensure we are in the right directory or change to it
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('../../') # Go up to workspace root
if os.path.exists(DIRECTORY):
    os.chdir(DIRECTORY)
else:
    print(f"Directory {DIRECTORY} not found!")
    sys.exit(1)

class Handler(http.server.SimpleHTTPRequestHandler):
    pass

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()
except OSError as e:
    print(f"Error: {e}")

