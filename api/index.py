import os
import sys
import shlex
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.append(os.path.join(os.environ["PWD"], "../main"))

from main import app

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        func = app.route("/articulos")(app.view_functions["articulos"])
        result = func()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(result)

httpd = HTTPServer(("0.0.0.0", int(os.environ["VERCEL_SERVERLESS_FUNCTION_NAME"].split("_")[-1])), Handler)
httpd.serve_forever()