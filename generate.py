import datetime
import json
import sys
from jinja2 import Template


def render_template(data, template_file_name, output_file_name):
    with open(template_file_name) as input, open(output_file_name, 'w') as output:
        template = Template(input.read())
        template.globals['now'] = datetime.datetime.utcnow
        output.write(template.render(machines = data))


def calculate_ips(machines):
    ip_blocks = machines['start_ip'].split('.')
    machines['cidr_block'] = ".".join(ip_blocks[:-1])

    start_ip = int(ip_blocks[-1])
    for i, role in enumerate(machines['nodes']):
        start = i * role_spread + start_ip
        role['start_ip'] = start
        role['end_blocks'] = [ start + i + 1 for i in range(role['count'])]
    return machines


# config values
role_spread = 10

if len(sys.argv) < 1:
    print("Usage: 'python generate.py <folder>' where folder contains a nodes.json config file")
    print("See README.md for details.")
    sys.exit(1)

folder = sys.argv[1]
machine_config_fine = folder + "/nodes.json"

with open(machine_config_fine) as config:
    raw_data = json.load(config)
    data = calculate_ips(raw_data)
    render_template(data, 'templates/Vagrantfile.j2', folder + '/Vagrantfile')
    render_template(data, 'templates/hosts.j2', folder + '/hosts.yml')
