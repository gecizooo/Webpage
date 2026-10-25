# Crypto License Shop (FastAPI)

Egyszerű FastAPI shop, ami kriptóval fogad el fizetést (NOWPayments), majd automatikusan kiadja a licenszet.

## Indítás

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Töltsd ki a .env fájlt (NOWPAYMENTS_API_KEY kötelező)

uvicorn app.main:app --reload
