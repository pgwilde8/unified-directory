#!/bin/bash
cd /opt/webwise/directory
source venv/bin/activate
exec uvicorn backend.main:app --host 0.0.0.0 --port 9178
