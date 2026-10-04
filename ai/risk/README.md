# Risk Scoring

Composite safety score across 4 categories:
- PPE Compliance (helmet + vest)
- Restricted Zones
- Equipment Safety
- Site Organization

Overall score = 100 - (weighted sum of violations / worker count)
Risk level: LOW (≥85) / MEDIUM (≥65) / HIGH (≥45) / CRITICAL (<45)

Implementation: `backend/app/services/scoring_service.py`
