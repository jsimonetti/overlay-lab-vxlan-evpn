#!/usr/bin/env python
import sys, getopt

"""
Runbook to configure datacenter
"""
from nornir.core import InitNornir
from nornir.plugins.functions.text import (
    print_result, print_title
)
from nornir.plugins.tasks.data import load_yaml
from nornir.plugins.tasks.networking import napalm_configure
from nornir.plugins.tasks.text import template_file


def configure(task):
    """
    This function groups all the tasks needed to configure the
    network:

        1. Load extra data
        2. Use templates to build configuration
        3. Deploy configuration on the devices
    """
    r = task.run(
        name="Base Configuration",
        task=template_file,
        template="base.j2",
        path=f"templates/{task.host.nos}",
        severity_level=0,
    )
    # r.result holds the result of rendering the template
    config = r.result

    r = task.run(
        name="Loading extra underlay data",
        task=load_yaml,
        file=f"extra_data/{task.host}/underlay.yaml",
        severity_level=0,
    )
    # r.result holds the data contained in the yaml files
    # we load the data inside the host itself for further use
    task.host["underlay"] = r.result

    r = task.run(
        name="Loading extra evpn data",
        task=load_yaml,
        file=f"extra_data/{task.host}/evpn.yaml",
        severity_level=0,
    )
    # r.result holds the data contained in the yaml files
    # we load the data inside the host itself for further use
    task.host["evpn"] = r.result

    r = task.run(
        name="Loading extra vxlan data",
        task=load_yaml,
        file=f"extra_data/{task.host}/vxlan.yaml",
        severity_level=0,
    )
    # r.result holds the data contained in the yaml files
    # we load the data inside the host itself for further use
    task.host["vxlan"] = r.result

    r = task.run(
        name="Interfaces Configuration",
        task=template_file,
        template="interfaces.j2",
        path=f"templates/{task.host.nos}",
        severity_level=0,
    )
    # we append the generated configuration
    config += r.result

    r = task.run(
        name="Routing Configuration",
        task=template_file,
        template="routing.j2",
        path=f"templates/{task.host.nos}",
        severity_level=0,
    )
    config += r.result

    r = task.run(
        name="EVPN Configuration",
        task=template_file,
        template="evpn.j2",
        path=f"templates/{task.host.nos}",
        severity_level=0,
    )
    config += r.result

    r = task.run(
        name="Role-specific Configuration",
        task=template_file,
        template=f"{task.host['role']}.j2",
        path=f"templates/{task.host.nos}",
        severity_level=0,
    )
    # we update our hosts' config
    config += r.result

    task.run(
        name="Loading Configuration on the device",
        task=napalm_configure,
        replace=True,
        configuration=config,
    )


# get dry-run flags
print_title("Parsing ARGS")
dryrun = True
try:
  for opt in sys.argv[1:]:
    if opt in ("-n", "--no-dry-run"):
      dryrun = False
except getopt.GetoptError:
    print(sys.argv[1:])
    dryrun = True


# Initialize nornir
nr = InitNornir(
    config_file="nornir.yaml", dry_run=dryrun, num_workers=20
)
if dryrun:
    print("Dry-run enabled")
else:
    print("Dry-run disabled. Updating devices")

# Let's just filter the hosts we want to operate on
cmh = nr.filter(type="network_device")

# Let's call the grouped tasks defined above
results = cmh.run(task=configure)

# Let's show everything on screen
print_title("Playbook to configure the network")
print_result(results)

