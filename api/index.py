import requests
import json
import uuid
import hashlib
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        username = query.get('u', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not username:
            self.wfile.write(json.dumps({"error": "Usage: /api?u=username", "dev": "@PyAnuj"}).encode())
            return

        # --- APKI SCRIPT SE NIKALE GAYE RESOURCES ---
        
        # 1. Device IDs Generate karna (Aapki script ka logic)
        device_id = 'android-' + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
        guid = str(uuid.uuid4())
        adid = str(uuid.uuid4())

        # 2. Mobile App Headers (Exact from your script)
        headers = {
            'User-Agent': 'Instagram 329.0.0.0.0 Android (33/13; 480dpi; 1080x2268; samsung; SM-S901E; r9q; qcom; en_US; 525000000)',
            'X-IG-App-ID': '936619743392459',
            'X-IG-Capabilities': '3brTvx0=',
            'X-IG-Connection-Type': 'WIFI',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        # 3. Recovery Flow Data (Aapki script ka main logic)
        # Ye check karta hai ki account password reset ke liye available hai ya nahi
        payload = {
            'signed_body': '0d067c2f86cac2c17d655631c9cec2402012fb0a329bcafb3b1f4c0bb56b1f1f.' + json.dumps({
                '_csrftoken': '9y3N5kLqzialQA7z96AMiyAKLMBWpqVj', # Dummy CSRF
                'adid': adid,
                'guid': guid,
                'device_id': device_id,
                'query': username,
                'client_input_params': json.dumps({'email_or_username': username})
            }),
            'ig_sig_key_version': '4',
        }

        try:
            # Step 1: Recovery Flow Check (More stable than profile info)
            recovery_url = 'https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/'
            response = requests.post(recovery_url, headers=headers, data=payload, timeout=10)
            res_json = response.json()

            # Logic: Agar "email_sent" ya success message hai toh Active hai
            if response.status_code == 200 or "email_sent" in str(res_json):
                result = {
                    "status": "Active ✅",
                    "username": username,
                    "method": "Mobile Recovery Flow",
                    "dev": "@PyAnuj",
                    "channel": "@itz_4nuj1"
                }
            elif "user_not_found" in str(res_json):
                result = {"status": "Banned/Not Found ❌", "username": username}
            else:
                # Fallback: Agar recovery flow fail ho toh normal info check karein
                info_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
                info_res = requests.get(info_url, headers=headers, timeout=5)
                if info_res.status_code == 200:
                    result = {"status": "Active ✅", "username": username}
                else:
                    result = {"status": "Banned ❌", "username": username}

        except Exception as e:
            result = {"status": "error", "message": str(e)}

        self.wfile.write(json.dumps(result, indent=4).encode())
