#!/usr/bin/env bash
# Checks your tools and your Azure login, creates an SSH key for the lab. Creates nothing in Azure. Run: ./setup.sh
set -u
cd "$(dirname "$0")"
bad=0
for c in az ssh-keygen curl python3; do command -v "$c" >/dev/null || { echo "MISSING: $c"; bad=1; }; done
[ "$bad" = 0 ] || { echo "Install what is missing and run ./setup.sh again."; exit 1; }
az account show >/dev/null 2>&1 || { echo "Not logged in to Azure. Run: az login"; exit 1; }
mkdir -p keys
[ -f keys/id_ed25519 ] || ssh-keygen -q -t ed25519 -N '' -C azure-lab -f keys/id_ed25519
chmod 600 keys/id_ed25519
IP=$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')
cat <<TXT
Ready.
  Subscription:   $(az account show --query name -o tsv)
  Resource group: rg-beanie-vm   (region: eastus)
  SSH key:        keys/id_ed25519 (public half: keys/id_ed25519.pub)
  Your public IP: $IP   (use $IP/32 in the SSH rule)
Nothing exists in Azure yet.
TXT
