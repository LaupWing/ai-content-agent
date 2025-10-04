import httpx
import os
from typing import Dict, Optional

# Get Laravel API config from environment
LARAVEL_API_URL = os.getenv("LARAVEL_API_URL", "http://localhost:8001/api")
LARAVEL_API_KEY = os.getenv("LARAVEL_API_KEY", "")

def _make_laravel_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Helper function to make requests to Laravel API"""
    url = f"{LARAVEL_API_URL}/{endpoint}"
    # headers = {"Authorization": f"Bearer {LARAVEL_API_KEY}"}
    headers = {"Authorization": f"Bearer xx"}
    
    try:
        if method == "GET":
            response = httpx.get(url, headers=headers, params=data, timeout=10.0)
            print(f"GET {url} - params: {data} - status: {response.status_code}")
            print(response.url)
        else:
            response = httpx.post(url, headers=headers, json=data, timeout=10.0)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}