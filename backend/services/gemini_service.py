import os
import json
import re
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    def load_dotenv(): pass

try:
    import httpx  # type: ignore
except ImportError:
    httpx = None

import urllib.request
import urllib.parse

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        self.endpoint_base = "https://generativelanguage.googleapis.com/v1beta/models"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_gemini_api_key_here")

    def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        raw_text = self.generate_text(prompt, system_instruction=system_instruction, json_mode=True)
        if not raw_text:
            return None

        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            json_match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except Exception:
                    pass
            print(f"[GEMINI_SERVICE WARNING] Failed to parse JSON from response snippet: {cleaned[:150]}")
            return None

    def generate_text(self, prompt: str, system_instruction: str = "", json_mode: bool = False) -> str:
        if not self.is_configured():
            print("[GEMINI_SERVICE WARNING] GEMINI_API_KEY is missing or unconfigured in .env!")
            return ""

        headers = {"Content-Type": "application/json"}
        
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction: {system_instruction}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will strictly follow these instructions."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 8192
            }
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        for model in self.models:
            url = f"{self.endpoint_base}/{model}:generateContent?key={self.api_key}"
            
            # Primary: use httpx if available
            if httpx is not None:
                try:
                    with httpx.Client(timeout=45.0) as client:
                        resp = client.post(url, json=payload, headers=headers)
                        if resp.status_code == 200:
                            data = resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts:
                                    return parts[0].get("text", "")
                        else:
                            print(f"[GEMINI_SERVICE WARNING] Model {model} returned HTTP {resp.status_code}: {resp.text[:200]}")
                except Exception as e:
                    print(f"[GEMINI_SERVICE ERROR] Request to model {model} failed: {e}")
            else:
                # Fallback: urllib standard library
                try:
                    req_data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
                    with urllib.request.urlopen(req, timeout=45.0) as resp:
                        if resp.status == 200:
                            data = json.loads(resp.read().decode("utf-8"))
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts:
                                    return parts[0].get("text", "")
                except Exception as e:
                    print(f"[GEMINI_SERVICE ERROR] urllib request to model {model} failed: {e}")

        return ""

gemini_service = GeminiService()
