# Vision-Language Model

Gemini 1.5 Flash (primary, free tier) or OpenAI GPT-4o-mini (fallback).
Receives image + YOLO hints + structured prompt, returns strict JSON.

Structured output includes: workers, helmets, vests, barriers, equipment,
restricted zones, scene observations, organization rating.

DeepSeek has no vision model — falls back to text-only reasoning.

Implementation: `backend/app/services/vlm_service.py`
