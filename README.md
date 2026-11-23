# ADUQT - Google jevo AI Search

## Potana computer par chalavvu

1. Python install karo, pachi aa folder ma terminal kholo.
2. `pip install -r requirements.txt`
3. API key set karo (console.anthropic.com parthi lo):
   - Windows: `set ANTHROPIC_API_KEY=tamari_key`
   - Mac/Linux: `export ANTHROPIC_API_KEY=tamari_key`
4. Brand nu naam badalva (optional): `set BRAND_NAME=TamaruNaam`
5. `python app.py` chalavo ane browser ma http://localhost:5000 kholo.

## Public karvu (internet par mukvu)

Render.com, Railway.app ke koi pan Python hosting par aa folder upload karo (GitHub dwara).
- Start command: `gunicorn app:app` (Procfile ma pehla thi chhe)
- Environment variables ma `ANTHROPIC_API_KEY` ane `BRAND_NAME` umero.
- API key kyarey code ke GitHub ma na lakho. Fakt environment variable ma rakho.

Potanu domain (jemke tamarunaam.com) kharidi ne hosting ma jodi shakay.

## Dhyan ma rakho

- Darek sawal par API no kharcho thay chhe. Hamna darek IP dithi 1 minute ma 10 sawal ni limit chhe (`RATE_LIMIT` thi badlay).
- Vadhare users aave to Anthropic console ma spending limit mukvi.
- Rate limit memory ma chhe, moti scale mate Redis jevu vapravu.
