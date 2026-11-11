#!/usr/bin/env bash
# Deletes the resource group and everything in it. Run with: ./teardown.sh
set -u
cd "$(dirname "$0")"
az account show >/dev/null 2>&1 || { echo "Not logged in to Azure (az login)." >&2; exit 1; }
if az group exists -n rg-beanie-vm | grep -q true; then
  echo "Deleting resource group rg-beanie-vm (a few minutes)..."
  az group delete -n rg-beanie-vm --yes
fi
rm -rf keys
echo "Now run ./verify-teardown.sh"
