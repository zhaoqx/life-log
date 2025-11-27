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
            # Default settings
            template_name = 'template1'
            user_id = 'eric' # Default user
            
            # Handle Template Param
            if 'template' in query_params:
                requested_template = query_params['template'][0]
                if requested_template in ['template1', 'simple', 'green']:
                    template_name = requested_template
            
            # Handle User Param
            if 'user' in query_params:
                user_id = query_params['user'][0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Load Data
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            
            # Select User Data
            # Note: We need to pass 'users' list for the switcher, and the specific user data for rendering
            user_data = all_data.get('users', {}).get(user_id, {})
            
            # If user not found, fallback to first available or empty
            if not user_data and 'users' in all_data:
                user_id = list(all_data['users'].keys())[0]
                user_data = all_data['users'][user_id]
            
            # Combine context: user_data + global assets + meta info for switcher
            context = user_data.copy()
            context['current_user'] = user_id
            context['current_template'] = template_name
            context['available_users'] = list(all_data.get('users', {}).keys())
            
            # Pass pdf_assets if needed globally
            if 'pdf_assets' in all_data:
                context['pdf_assets'] = all_data['pdf_assets']

            # Render Template
            try:
                template = env.get_template(f'{template_name}.html')
                rendered_html = template.render(**context)
                self.wfile.write(rendered_html.encode('utf-8'))
            except Exception as e:
                self.wfile.write(f"Error rendering template: {e}".encode('utf-8'))
            return
            
        # Serve static files (images, css) normally
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

print(f"Starting server at http://localhost:{PORT}")
print(f"Templates loaded from: {TEMPLATE_DIR}")
print(f"Serving content from: {WEB_BUILD_DIR}")

try:
    with socketserver.TCPServer(("", PORT), TemplateHandler) as httpd:
        httpd.serve_forever()
except OSError as e:
    print(f"Error: {e}")

