#!/bin/sh
# Backend health check script used by Docker
curl -f http://localhost:8000/health || exit 1
