import ansible_runner
import tempfile
import os
# YAML content as a string
playbook_content = """---
- name: Deploy 3 NGINX pods to Kubernetes
  hosts: localhost
  gather_facts: no
  collections:
    - community.kubernetes
  tasks:
    - name: Create NGINX Deployment
      k8s:
        state: present
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: nginx-deployment
            namespace: default
          spec:
            replicas: 3
            selector:
              matchLabels:
                app: nginx
            template:
              metadata:
                labels:
                  app: nginx
              spec:
                containers:
                  - name: nginx
                    image: nginx:latest
                    ports:
                      - containerPort: 80
"""
def run_inline_playbook(playbook_text):
    with tempfile.TemporaryDirectory() as tmpdir:
        playbook_path = os.path.join(tmpdir, 'deploy_nginx.yaml')
        # Write playbook to file
        with open(playbook_path, 'w') as f:
            f.write(playbook_text)
        # Run the playbook
        result = ansible_runner.run(private_data_dir=tmpdir, playbook='deploy_nginx.yaml')
        print(f"Status: {result.status}")
        print(f"RC: {result.rc}")
        if result.rc != 0:
            print("Playbook execution failed!")
        else:
            print("Playbook executed successfully!")
        # Optional: Print stdout lines
        for event in result.events:
            if 'stdout' in event:
                print(event['stdout'])
if __name__ == "__main__":
    run_inline_playbook(playbook_content)