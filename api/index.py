from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract username from query (?u=username)
        query = parse_qs(urlparse(self.path).query)
        username = query.get('u', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # CORS allow taaki tum ise kahin bhi use kar sako
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not username:
            error_res = {
                "status": "error",
                "message": "Please provide a username. Usage: /api?u=username",
                "dev": "@PyAnuj"
            }
            self.wfile.write(json.dumps(error_res).encode())
            return

        # VIP Headers for bypassing simple blocks
        headers = {
            'User-Agent': 'Instagram 329.0.0.0.0 Android (33/13; 480dpi; 1080x2268; samsung; SM-S901E; r9q; qcom; en_US; 525000000)',
            'X-IG-App-ID': '936619743392459',
            'X-ASBD-ID': '129477',
            'X-IG-WWW-Claim': '0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('data', {}).get('user')
                
                if user:
                    result = {
                        "status": "success",
                        "account_status": "Active ✅",
                        "data": {
                            "username": username,
                            "id": user.get('id'),
                            "full_name": user.get('full_name'),
                            "is_private": user.get('is_private'),
                            "is_verified": user.get('is_verified'),
                            "followers": user.get('edge_followed_by', {}).get('count'),
                            "following": user.get('edge_follow', {}).get('count')
                        },
                        "credits": {
                            "dev": "@PyAnuj",
                            "channel": "@itz_4nuj1"
                        }
                    }
                else:
                    result = {"status": "fail", "account_status": "Banned/Deleted ❌"}
            
            elif response.status_code == 404:
                result = {"status": "fail", "account_status": "Banned/Not Found ❌"}
            
            elif response.status_code == 429:
                result = {"status": "error", "message": "Rate Limited by Instagram. Use Proxy."}
            
            else:
                result = {"status": "error", "message": f"Instagram returned status {response.status_code}"}

        except Exception as e:
            result = {"status": "error", "message": str(e)}

        self.wfile.write(json.dumps(result, indent=4).encode())
