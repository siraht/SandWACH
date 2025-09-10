#!/usr/bin/env python3
"""
SandWACH API Server
Simple HTTP server with recommendations endpoint and MCP support
"""

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

from config import API_HOST, API_PORT, API_KEY_REQUIRED
from weather import fetch_weather_data
from decisions import analyze_sleep_conditions, analyze_daytime_conditions

class SandWACHRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for SandWACH API"""

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query = parse_qs(parsed_path.query)

            # Check API key for external access
            api_key = self.headers.get('X-API-Key', '')
            if path.startswith('/api/') and api_key != API_KEY_REQUIRED:
                self.send_error(401, "Invalid API key")
                return

            if path == '/api/recommendations':
                self.handle_recommendations(query)
            elif path == '/health':
                self.handle_health()
            else:
                self.send_error(404, "Endpoint not found")

        except Exception as e:
            print(f"Request error: {e}")
            self.send_error(500, "Internal server error")

    def do_POST(self):
        """Handle POST requests (for MCP)"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                try:
                    request_data = json.loads(body)
                    self.handle_mcp_request(request_data)
                except json.JSONDecodeError:
                    self.send_error(400, "Invalid JSON")
            else:
                self.send_error(400, "No request body")

        except Exception as e:
            print(f"POST request error: {e}")
            self.send_error(500, "Internal server error")

    def handle_recommendations(self, query):
        """Handle recommendations API endpoint"""
        try:
            # Get analysis type from query parameters
            analysis_type = query.get('type', ['sleep'])[0]

            # Fetch weather data
            weather_data = fetch_weather_data()
            if not weather_data:
                self.send_json_response(503, {"error": "Weather service unavailable"})
                return

            # Perform analysis
            if analysis_type == 'sleep':
                recommendations = analyze_sleep_conditions(weather_data)
            elif analysis_type == 'day':
                recommendations = analyze_daytime_conditions(weather_data)
            else:
                self.send_json_response(400, {"error": "Invalid analysis type. Use 'sleep' or 'day'"})
                return

            self.send_json_response(200, recommendations)

        except Exception as e:
            print(f"Recommendations error: {e}")
            self.send_json_response(500, {"error": "Analysis failed"})

    def handle_health(self):
        """Handle health check endpoint"""
        health_status = {
            "status": "healthy",
            "timestamp": int(time.time()),
            "service": "SandWACH",
            "version": "1.0.0"
        }
        self.send_json_response(200, health_status)

    def handle_mcp_request(self, request_data):
        """Handle MCP (Model Context Protocol) requests"""
        try:
            method = request_data.get('method', '')
            params = request_data.get('params', {})

            response = {"jsonrpc": "2.0", "id": request_data.get('id')}

            if method == "sandwach.get_weather":
                weather_data = fetch_weather_data()
                if weather_data:
                    response["result"] = weather_data
                else:
                    response["error"] = {"code": -32000, "message": "Weather service unavailable"}

            elif method == "sandwach.get_recommendations":
                analysis_type = params.get('type', 'sleep')
                weather_data = fetch_weather_data()

                if weather_data:
                    if analysis_type == 'sleep':
                        recommendations = analyze_sleep_conditions(weather_data)
                    else:
                        recommendations = analyze_daytime_conditions(weather_data)
                    response["result"] = recommendations
                else:
                    response["error"] = {"code": -32000, "message": "Weather service unavailable"}

            elif method == "sandwach.get_health":
                response["result"] = {
                    "status": "healthy",
                    "timestamp": int(time.time()),
                    "service": "SandWACH"
                }

            else:
                response["error"] = {"code": -32601, "message": "Method not found"}

            self.send_json_response(200, response)

        except Exception as e:
            print(f"MCP request error: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": request_data.get('id'),
                "error": {"code": -32603, "message": "Internal error"}
            }
            self.send_json_response(500, error_response)

    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-API-Key, Content-Type')
        self.end_headers()

        json_response = json.dumps(data, indent=2)
        self.wfile.write(json_response.encode('utf-8'))

    def log_message(self, format, *args):
        """Override to use print instead of logging"""
        print(f"[API] {format % args}")

def start_api_server():
    """Start the API server"""
    server_address = (API_HOST, API_PORT)
    httpd = HTTPServer(server_address, SandWACHRequestHandler)
    print(f"SandWACH API server running on http://{API_HOST}:{API_PORT}")
    print(f"Health endpoint: http://{API_HOST}:{API_PORT}/health")
    print(f"Recommendations endpoint: http://{API_HOST}:{API_PORT}/api/recommendations?type=sleep")
    httpd.serve_forever()

# Test functions
if __name__ == "__main__":
    print("Starting SandWACH API server...")
    try:
        start_api_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
