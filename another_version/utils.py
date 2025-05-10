import yaml
import subprocess
import jinja2
import uuid
import os

def load_yaml_file(file_path):
    """Load and parse a YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def render_template(template_path, input_data):
    """Render a Jinja2 template with the given input data."""
    loader = jinja2.FileSystemLoader(searchpath="./")
    environment = jinja2.Environment(loader=loader)
    template = environment.get_template(template_path)
    return template.render(input=input_data)

def generate_playbook_file(content):
    """Generate a playbook file with the given content."""
    file_name = f"/tmp/playbook-{str(uuid.uuid1())[:4]}.yaml"
    with open(file_name, "w") as file:
        file.write(content)
    return file_name

def build_playbook(pre_playbook_path):
    """Build a playbook from a pre-playbook YAML file."""
    input_data = load_yaml_file(pre_playbook_path)
    content = render_template('playbook.jinja2', input_data)
    playbook_file = generate_playbook_file(content)
    print(f'Content of playbook file {playbook_file}:')
    print(content)
    return playbook_file

def run_ansible_playbook(inventory_file, playbook_file):
    """Run an Ansible playbook with the given inventory file and playbook file."""
    ansible_command = f"ansible-playbook -v -i {inventory_file} {playbook_file}"
    print(ansible_command)
    result = subprocess.run(["sh", "-c", ansible_command])
    return result.returncode
