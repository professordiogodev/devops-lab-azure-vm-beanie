#!/usr/bin/env python3
import json, os, socket, subprocess, sys, time, urllib.request, urllib.error
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
RG, LAB = "rg-beanie-vm", "azure-vm-beanie"
passed = failed = 0


def check(desc, ok, hint=""):
    global passed, failed
    if ok:
        passed += 1; print("PASS  " + desc)
    else:
        failed += 1; print("FAIL  " + desc + (("   -> " + hint) if hint else ""))


def az(*a, timeout=180):
    try:
        out = subprocess.run(("az",) + a + ("-o", "json"), capture_output=True, text=True, timeout=timeout)
        return json.loads(out.stdout) if out.returncode == 0 and out.stdout.strip() else None
    except Exception:
        return None


def finish():
    print()
    print(("ALL CHECKS PASSED (%d/%d)" % (passed, passed)) if failed == 0 else ("%d check(s) failed, %d passed" % (failed, passed)))
    sys.exit(1 if failed else 0)


def http(url, data=None, timeout=10):
    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def port_open(ip, port, t=5):
    try:
        s = socket.create_connection((ip, port), timeout=t); s.close(); return True
    except Exception:
        return False


sub = (az("account", "show") or {}).get("name")
print("Subscription %s" % sub)
print("== The resource group ==")
rg = az("group", "show", "-n", RG)
check("resource group %s exists" % RG, bool(rg), "az group create -n %s -l eastus --tags lab=%s" % (RG, LAB))
if not rg:
    finish()
check("the resource group is tagged lab=%s" % LAB, (rg.get("tags") or {}).get("lab") == LAB)
vms = az("vm", "list", "-g", RG, "-d") or []
check("one virtual machine", len(vms) == 1)
if len(vms) != 1:
    finish()
vm = vms[0]
check("a small size (B-series, or a 2-vCPU D/A/F size if B is restricted in your subscription)", vm["hardwareProfile"]["vmSize"].startswith(("Standard_B", "Standard_D2", "Standard_DS1", "Standard_A", "Standard_F2")), vm["hardwareProfile"]["vmSize"])
img = vm["storageProfile"]["imageReference"]
check("image is Ubuntu 24.04 LTS from Canonical", img.get("publisher", "").lower() == "canonical" and "24_04" in img.get("offer", ""))
lc = vm["osProfile"].get("linuxConfiguration", {})
check("password authentication is disabled and one SSH public key is set", lc.get("disablePasswordAuthentication") is True and len(lc.get("ssh", {}).get("publicKeys", [])) == 1)
check("no data disks, a managed OS disk", not vm["storageProfile"].get("dataDisks") and vm["storageProfile"]["osDisk"].get("managedDisk"))

print("== The network and the firewall ==")
nsgs = az("network", "nsg", "list", "-g", RG) or []
check("a Network Security Group exists", len(nsgs) >= 1)
allow = []
for n in nsgs:
    for r in n.get("securityRules", []):
        if r["direction"] == "Inbound" and r["access"] == "Allow":
            ports = ([r["destinationPortRange"]] if r.get("destinationPortRange") else []) + r.get("destinationPortRanges", [])
            srcs = ([r["sourceAddressPrefix"]] if r.get("sourceAddressPrefix") else []) + r.get("sourceAddressPrefixes", [])
            allow.append((r["priority"], ports, srcs))
anyp = ("*", "Internet", "0.0.0.0/0", "Any")
ssh = [a for a in allow if "22" in a[1]]
check("SSH (22) is allowed from exactly one /32 address, never from * or Internet", len(ssh) == 1 and len(ssh[0][2]) == 1 and ssh[0][2][0].endswith("/32") and ssh[0][2][0] not in anyp, str(ssh))
web = [a for a in allow if "8000" in a[1]]
check("port 8000 is allowed from the internet", len(web) == 1 and any(s in anyp for s in web[0][2]))
other = [a for a in allow if not set(a[1]) <= {"22", "8000"}]
check("nothing else is allowed in (no 8001-8004, no *)", not other, str(other))
attached = any(n.get("subnets") or n.get("networkInterfaces") for n in nsgs)
check("the NSG is attached to the subnet or to the network interface", attached)
pips = az("network", "public-ip", "list", "-g", RG) or []
check("one public IP, Standard SKU, static", len(pips) == 1 and pips[0]["sku"]["name"] == "Standard" and pips[0]["publicIPAllocationMethod"] == "Static")
if len(pips) != 1:
    finish()
ip = pips[0].get("ipAddress")

print("== Live, from the internet ==")
check("SSH port 22 is reachable from here (the /32 rule has YOUR current address)", port_open(ip, 22), "your IP may have changed: curl https://checkip.amazonaws.com")
st = 0
end = time.time() + 600
while time.time() < end:
    st, body = http("http://%s:8000/api/menu" % ip)
    if st == 200:
        break
    time.sleep(10)
check("GET http://%s:8000/api/menu answers 200 (cloud-init can take 3-6 minutes)" % ip, st == 200, "az vm run-command invoke ... 'tail -50 /var/log/cloud-init-output.log'")
st, body = http("http://%s:8000/api/orders" % ip, json.dumps({"customer": "Ana", "items": [{"item_id": "flat-white", "quantity": 2}]}).encode())
check("POST /api/orders is paid (201)", st == 201, "got %s" % st)
check("ports 8001, 8002, 8003 and 8004 are NOT reachable from the internet", not any(port_open(ip, p, 4) for p in (8001, 8002, 8003, 8004)))
rc = az("vm", "run-command", "invoke", "-g", RG, "-n", vm["name"], "--command-id", "RunShellScript", "--scripts",
        "for s in gateway menu orders payments notifications; do echo $s $(systemctl is-active beanie@$s) $(systemctl is-enabled beanie@$s); done; ps -eo user:20,args | grep 'beanie' | grep -v grep | awk '{print $1}' | sort -u", timeout=240)
msg = (rc or {}).get("value", [{}])[0].get("message", "")
check("five beanie@ services are active and enabled at boot", all(("%s active enabled" % s) in msg for s in ("gateway", "menu", "orders", "payments", "notifications")), msg[-200:])
users = [l.strip() for l in msg.split("\n") if l.strip() and " " not in l.strip() and not l.startswith("[")]
check("the services do not run as root", "root" not in users and "beanie" in msg, "users seen: %s" % users)
finish()
