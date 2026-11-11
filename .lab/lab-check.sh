#!/usr/bin/env bash
rc=0
grep -q '^#cloud-config' cloud-init.yaml && echo "- ✅ cloud-init.yaml starts with #cloud-config" || { echo "- ❌ cloud-init.yaml must start with #cloud-config"; rc=1; }
grep -qE '^\s*runcmd:' cloud-init.yaml && grep -q 'beanie@' cloud-init.yaml && echo "- ✅ cloud-init.yaml starts the beanie@ services" || { echo "- ❌ cloud-init.yaml has no runcmd that starts beanie@... services"; rc=1; }
git ls-files | grep -q '^keys/' && { echo "- ❌ keys/ is committed"; rc=1; } || echo "- ✅ no SSH key committed"
grep -rEq 'BEGIN (OPENSSH|RSA) PRIVATE KEY' . --exclude-dir=.git --exclude-dir=keys && { echo "- ❌ a private key is committed"; rc=1; } || echo "- ✅ no private key committed"
grep -qE '^ALL CHECKS PASSED \(' SUBMISSION.md && echo "- ✅ SUBMISSION.md shows ALL CHECKS PASSED" || { echo "- ❌ paste the verify.sh output ('ALL CHECKS PASSED') into SUBMISSION.md"; rc=1; }
exit $rc
