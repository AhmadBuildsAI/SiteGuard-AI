"""
Multi-provider VLM client using OpenAI SDK (vision mode).
Fallback to text-only reasoning when provider lacks vision.
"""
from openai import OpenAI
from typing import Optional, Dict
import base64, json
from .config import settings


PROVIDERS = {
    "gemini":   {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "default_model": "gemini-1.5-flash", "vision": True},
    "openai":   {"base_url": None, "default_model": "gpt-4o-mini", "vision": True},
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "default_model": "deepseek-chat", "vision": False},
}


class VLMClient:
    def __init__(self):
        self.enabled = bool(settings.VLM_API_KEY)
        self.provider = settings.VLM_PROVIDER.lower()
        self.model = settings.VLM_MODEL or PROVIDERS.get(self.provider, {}).get("default_model", "gpt-4o-mini")
        self.has_vision = PROVIDERS.get(self.provider, {}).get("vision", False)
        self.client = None
        
        if self.enabled:
            cfg = PROVIDERS.get(self.provider)
            if cfg:
                self.client = OpenAI(api_key=settings.VLM_API_KEY, base_url=cfg["base_url"])
                print(f"✅ VLM ready: provider={self.provider}, model={self.model}, vision={self.has_vision}")
            else:
                print(f"⚠️  Unknown provider '{self.provider}' — VLM disabled")
                self.enabled = False
        else:
            print("⚠️  No VLM_API_KEY — using deterministic fallback (YOLO + rules only)")
    
    def analyze_image(self, image_b64: str, yolo_summary: str, prompt: str) -> Dict:
        """Send image + context to VLM, expect JSON response."""
        if not self.enabled or not self.has_vision:
            return {"error": "vlm_unavailable"}
        
        try:
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"YOLO detector found: {yolo_summary}\n\nAnalyze this construction site image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                ]},
            ]
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.VLM_TEMPERATURE,
                max_tokens=settings.VLM_MAX_TOKENS,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            return json.loads(raw)
        except Exception as e:
            print(f"VLM error: {e}")
            return {"error": str(e)[:200]}
    
    def chat_text(self, system: str, user: str) -> str:
        """Text-only fallback (used when provider has no vision)."""
        if not self.enabled or not self.client:
            return ""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=settings.VLM_TEMPERATURE,
                max_tokens=settings.VLM_MAX_TOKENS,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM error: {e}")
            return ""


vlm_client = VLMClient()
