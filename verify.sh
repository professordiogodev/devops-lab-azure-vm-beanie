#!/usr/bin/env bash
# Reads what you built in Azure and uses it from the internet. Run with: ./verify.sh
cd "$(dirname "$0")" || exit 1
az account show >/dev/null 2>&1 || { echo "Not logged in to Azure (az login)." >&2; exit 1; }
exec python3 .lab/azcheck.py
