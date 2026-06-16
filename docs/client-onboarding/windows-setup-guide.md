# SME Analytics — Windows Setup Guide

**Time to first dashboard: ~15 minutes**

---

## What You Need

- Windows 10 or 11 (64-bit)
- Python 3.11 or 3.12 — download from [python.org](https://python.org) (tick "Add to PATH" during install)
- The SME Analytics folder provided by AgriSolve

---

## Step 1 — Open Terminal

Press **Win + R**, type `cmd`, press Enter.

Navigate to the SME Analytics folder:
```
cd "C:\SME Analytics"
```

---

## Step 2 — Create a Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt.

---

## Step 3 — Install Dependencies

```
pip install -r requirements.txt
```

This takes 2–5 minutes the first time.

---

## Step 4 — Launch the Dashboard

```
run.bat
```

Or manually:
```
streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**

---

## Step 5 — Load Your Data

1. Select your **business vertical** from the dropdown (Insurance Broker, Accounting, etc.)
2. Choose **Demo data** to see the dashboard with sample data
3. Choose **Upload my data** to load your real CSV files
4. Use the CSV templates in this folder as a guide for column names and formats

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not found | Re-install Python and tick "Add to PATH" |
| `pip` errors on install | Run: `python -m pip install --upgrade pip` first |
| Port 8501 in use | Change port: `streamlit run app.py --server.port 8502` |
| CSV validation errors | Check column names match the template exactly (case-sensitive) |

---

## Monthly Routine

1. Export your data files from your source systems
2. Double-click `run.bat` (or run `streamlit run app.py`)
3. Upload your CSV files
4. Review exceptions and export your report

---

**Support:** adriaan.h.pienaar@gmail.com · 074 666 8673
