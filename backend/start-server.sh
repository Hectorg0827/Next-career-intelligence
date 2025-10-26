#!/bin/sh
# Startup script for Cloud Run
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
