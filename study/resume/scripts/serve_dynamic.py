import http.server
import socketserver
import os
import json
import urllib.parse
from jinja2 import Environment, FileSystemLoader

PORT = 5025
WEB_BUILD_DIR = os.path.join('study', 'resume', 'web_build')
TEMPLATE_DIR = os.path.join('study', 'resume', 'web_templates')

# Jinja2 Setup
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# Ensure Data exists
DATA_FILE = os.path.join(WEB_BUILD_DIR, 'data.json')
if not os.path.exists(DATA_FILE):
    print("Error: data.json not found. Run update_web_resume.py first.")
    exit(1)

class TemplateHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_BUILD_DIR, **kwargs)

    def do_GET(self):
        # Parse query params
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            # Default template
            template_name = 'template1'
            if 'template' in query_params:
                requested_template = query_params['template'][0]
                if requested_template in ['template1', 'simple', 'green']:
                    template_name = requested_template
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Load Data
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Render Template
            try:
                template = env.get_template(f'{template_name}.html')
                rendered_html = template.render(**data)
                self.wfile.write(rendered_html.encode('utf-8'))
            except Exception as e:
                self.wfile.write(f"Error rendering template: {e}".encode('utf-8'))
            return
            
        # Serve static files (images, css) normally
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

print(f"Starting server at http://localhost:{PORT}")
print(f"Templates loaded from: {TEMPLATE_DIR}")
print(f"Serving content from: {WEB_BUILD_DIR}")

# Change to workspace root for correct relative paths if needed
# Actually SimpleHTTPRequestHandler directory arg handles it
try:
    with socketserver.TCPServer(("", PORT), TemplateHandler) as httpd:
        httpd.serve_forever()
except OSError as e:
    print(f"Error: {e}")

