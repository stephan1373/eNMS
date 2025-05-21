from orjson import dumps
from pathlib import Path
from random import choice, randrange

PATH = (
    Path.cwd().parent.parent.parent
    / "eNMS-prod2"
    / "files"
    / "migrations"
    / "scalability"
)

def generate_devices():
    with open(PATH / "generic_device.json", "wb") as file:
        file.write(dumps([
        {"name": f"Device{index}", "model": f"Model{randrange(1, 21)}"}
        for index in range(150_000)
    ]))

def generate_links():
    with open(PATH / "generic_link.json", "wb") as file:
        file.write(dumps([
            {"name": f"Link{index}", "model": f"Model{randrange(1, 51)}"}
            for index in range(30_000)
        ]))

def generate_services():
    with open(PATH / "swiss_army_knife_service.json", "wb") as file:
        file.write(dumps([
            {
                "name": "[Shared] Start",
                "scoped_name": "Start",
                "shared": True,
            },
            {
                "name": "[Shared] End",
                "scoped_name": "End",
                "shared": True,
            },
            {
                "name": "[Shared] Placeholder",
                "scoped_name": "Placeholder",
                "shared": True,
            }
        ]))
    with open(PATH / "python_snippet_service.json", "wb") as file:
        file.write(dumps([
            {
                "name": f"[Shared] Service{index}",
                "model": f"Model{randrange(1, 21)}",
                "vendor": choice(["Cisco", "Juniper", "Arista"]),
                "scoped_name": f"Service{index}",
                "shared": True
            } for index in range(9_997)
        ]))

def generate_workflows():
    workflows = []
    for index in range(2_000):
        positions = {"[Shared] Start": [0, 0], "[Shared] End": [2200, 400]}
        for i in range(10):
            positions[f"[Shared] Service{index + i}"] = ((i + 1) * 200, 0)
            positions[f"[Shared] Service{index + i + 10}"] = (2000 - 200 * i, 200)
            positions[f"[Shared] Service{index + i + 20}"] = ((i + 1) * 200, 400)
        workflows.append({
            "name": f"[Shared] Workflow{index}",
            "positions": positions,
            "vendor": choice(["Cisco", "Juniper", "Arista"]),
            "scoped_name": f"Workflow{index}",
            "shared": True,
        })
    with open(PATH / "workflow.json", "wb") as file:
        file.write(dumps(workflows))

def generate_workflow_association_table():
    association_table = []
    for j in range(2000):
        association_table.append(["[Shared] Start", f"[Shared] Workflow{j}"])
        association_table.append(["[Shared] End", f"[Shared] Workflow{j}"])
        for i in range(j, j + 30):
            association_table.append([f"[Shared] Service{i}", f"[Shared] Workflow{j}"]) 
    with open(PATH / "service_workflow_table.json", "wb") as file:
        file.write(dumps(association_table))

def generate_tasks():
    with open(PATH / "task.json", "wb") as file:
        file.write(dumps([
            {"name": f"Task{index}", "is_active": choice([True, False])}
            for index in range(2_000)
        ]))

def generate_pools():
    pools = []
    for index in range(2_000):
        if index < 1000:
            pools.append({"name": f"Pool{index}", "manually_defined": True})
        else:
            start_range = randrange(1, 150)
            pools.append(
                {
                    "name": f"Pool{index}",
                    "device_name": f"Device{start_range}\d{3}",
                    "device_name_match": "regex",
                }
            )
    with open(PATH / "pool.json", "wb") as file:
        file.write(dumps(pools))

def generate_users():
    users = [{"name": f"user{index}"} for index in range(1, 1_001)]
    with open(PATH / "user.json", "wb") as file:
        file.write(dumps(users))

def generate_networks():
    networks = [
        {
            "name": f"w{index}",
            "devices": list(set(f"d{randrange(1, 80_000)}" for _ in range(30))),
        }
        for index in range(1, 1_001)
    ]
    with open(PATH / "network.json", "wb") as file:
        file.write(dumps(networks))


generate_devices()
generate_links()
generate_services()
generate_workflows()
generate_workflow_association_table()
