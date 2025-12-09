@echo off
cd /d "C:\Users\rubenurbano\HIPERTEX"
uvicorn ipc_api:app --host 127.0.0.1 --port 8000 --reload
