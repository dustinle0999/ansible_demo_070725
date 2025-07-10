#!/usr/bin/env python3

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
        sys.exit(f"{name} not found in /{endpoint}/")
    return data["results"][0]["id"]

def sync_project(project_id: int) -> None:
    """Sync the project to ensure latest code is available"""
    print(f"Syncing project {project_id}...")
    sync_payload = {}
    sync_response = requests.post(f"{API}/projects/{project_id}/update/", 
                                 json=sync_payload, headers=HEADERS, verify=False, timeout=30)
    sync_response.raise_for_status()
    print("Project sync initiated successfully")
    print("Waiting for 10 seconds to ensure the project is synced")
    time.sleep(10)

def execute_job(job_template_id: int) -> int:
    """Execute a job template and return the job ID"""
    print(f"Executing job template {job_template_id}...")
    job_payload = {}
    job_response = requests.post(f"{API}/job_templates/{job_template_id}/launch/", 
                                json=job_payload, headers=HEADERS, verify=False, timeout=30)
    job_response.raise_for_status()
    job_id = job_response.json()["job"]
    print(f"Job {job_id} launched successfully")
    return job_id

# Get required IDs
inv_id         = id_by_name("inventories",  "Demo Inventory")
proj_id        = id_by_name("projects",     "dustin_sample_repo")
cred_users_id  = id_by_name("credentials",  "OpenShift User")

# Sync project before creating job template
sync_project(proj_id)

# Create job template
payload = {
    "name":          f"nginx-demo-{int(time.time())}",
    "job_type":      "run",
    "inventory":     inv_id,
    "project":       proj_id,
    "playbook":      "ocp_deployment_ngix_v1.yml",
    "credential":    cred_users_id,
    "extra_vars": """
""",
}

jt = requests.post(f"{API}/job_templates/", json=payload, headers=HEADERS, verify=False, timeout=30)
jt.raise_for_status()
jt_id = jt.json()["id"]
print(f"Job Template {jt_id} created")

# Attach the second credential (multi-credential endpoint)
assoc = {"associate": True, "id": cred_users_id}
requests.post(f"{API}/job_templates/{jt_id}/credentials/", json=assoc,
              headers=HEADERS, verify=False, timeout=30).raise_for_status()

# Execute the job
job_id = execute_job(jt_id)
print(f"Job execution completed. Job ID: {job_id}")