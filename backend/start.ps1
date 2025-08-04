# PowerShell script to start the FastAPI backend with improved code

# Activate environment if needed
# .\venv\Scripts\Activate.ps1

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
