#!/usr/bin/env python3
"""
Create a Job Template called “nginx-demo-<epoch>” that:

* job_type        = run
* inventory       = Demo Inventory
* project         = dustin_sample_repo
* playbook        = ocp_deployment_ngix.yml
* credentials     = [OpenShift User]
* extra_vars      = ocp_api_host / ocp_namespace / num_replica
"""

import os, sys, time, requests, urllib.parse

AAP_HOST = "https://rfp-aap-aap.apps.itz-o8poc6.hub01-lb.techzone.ibm.com"
TOKEN    = "uSBqQ8g3Qu0gLrgnSC6AQHKkLovXWf"

#AAP_HOST = os.environ["AAP_HOST"]          # e.g. https://aap.example.com
#TOKEN    = os.environ["AAP_TOKEN"]         # controller PAT

API      = f"{AAP_HOST.rstrip('/')}/api/controller/v2"
HEADERS  = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def id_by_name(endpoint: str, name: str) -> int:
    q = urllib.parse.quote_plus(name)
    r = requests.get(f"{API}/{endpoint}/?name={q}", headers=HEADERS, verify=False, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data["count"] == 0:
        sys.exit(f"❌  {name} not found in /{endpoint}/")
    return data["results"][0]["id"]

inv_id         = id_by_name("inventories",  "Demo Inventory")
proj_id        = id_by_name("projects",     "dustin_sample_repo")
cred_users_id  = id_by_name("credentials",  "OpenShift User")

payload = {
    "name":          f"nginx-demo-{int(time.time())}",
    "job_type":      "run",
    "inventory":     inv_id,
    "project":       proj_id,
    "playbook":      "ocp_deployment_ngix_v1.yml",
    "credential":    cred_users_id,               # primary credential
    "extra_vars": """
ocp_api_host: https://api.itz-o8poc6.hub01-lb.techzone.ibm.com:6443
ocp_namespace: nginx-demo
num_replica: 2
""",
}

jt = requests.post(f"{API}/job_templates/", json=payload, headers=HEADERS, verify=False, timeout=30)
jt.raise_for_status()
jt_id = jt.json()["id"]
print(f"✅  Created Job Template {jt_id}")

# Attach the second credential (multi-credential endpoint)
assoc = {"associate": True, "id": cred_users_id}
requests.post(f"{API}/job_templates/{jt_id}/credentials/", json=assoc,
              headers=HEADERS, verify=False, timeout=30).raise_for_status()
print("✅  Associated OpenShift Users credential")
