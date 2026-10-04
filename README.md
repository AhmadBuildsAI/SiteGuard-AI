# 🏗️ SiteGuard AI — Construction Site Safety & Progress Monitoring

A Vision-Language AI platform that analyzes construction-site images and produces explainable safety observations.

## ⚠️ CRITICAL DISCLAIMER

**SiteGuard AI is a decision-support tool, NOT an automated enforcement system.**

- All alerts are **potential observations**, not confirmed violations
- Every alert explicitly requires **human safety inspector verification**
- The system does NOT identify individual workers
- The system must NOT be used for automated disciplinary action
- Construction safety decisions require on-site human judgment

## 🎯 Features

- **Multi-format Ingestion** — JPG, PNG, WebP
- **YOLO Detection** — pretrained YOLOv8n (person, vehicle) — optional
- **VLM Scene Analysis** — Gemini 1.5 Flash or GPT-4o-mini vision
- **Safety Rule Engine** — 6 deterministic rules (helmet, vest, zone, equipment, barrier, organization)
- **Explainable Evidence** — every alert shows bounding boxes + VLM observation + rule ID
- **Safety Score** — composite across 4 categories
- **Alert Center** — severity-ranked, acknowledge workflow
- **Site History** — all past inspections

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript + Tailwind + Recharts |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL 15 |
| Detection | Ultralytics YOLOv8n (optional) |
| VLM | Gemini 1.5 Flash / GPT-4o-mini |
| Rule Engine | Deterministic Python |
| Deployment | Docker + Docker Compose |

## 🧠 Pipeline



## 🔍 Validation

The delivered source was checked for Python syntax and the deterministic safety pipeline was smoke-tested against a synthetic scenario that triggers all six safety rules. Frontend dependency installation/build and Docker runtime require a network-enabled Docker/Node environment and should be run locally with the commands below.

```bash
docker compose up --build
```

Then open `http://localhost:3000`. API documentation is available at `http://localhost:8000/docs`.

## 🔐 Demo credentials

- Email: `admin@siteguard.com`
- Password: `admin123`

Change the secret and demo credentials before any real deployment.
