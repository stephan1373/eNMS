from orjson import dumps
from pathlib import Path
from random import randrange

PATH = (
    Path.cwd().parent.parent.parent
    / "eNMS-prod2"
    / "files"
    / "migrations"
    / "scalability"
)

def generate_services():
    services = [
        {
            "name": f"[Shared] s{index}",
            "model": f"Model{randrange(1, 21)}",
            "scoped_name": f"s{index}",
            "shared": True,
            "type": "python_snippet_service",
        }
        for index in range(10_000)
    ]
    with open(PATH / "python_snippet_service.json", "wb") as file:
        file.write(dumps(services))
    workflows = [
        {
            "name": f"[Shared] w{index}",
            "scoped_name": f"w{index}",
            "shared": True,
            "type": "workflow",
        }
        for index in range(2_000)
    ]
    with open(PATH / "workflow.json", "wb") as file:
        file.write(dumps(workflows))

def generate_devices():
    with open(PATH / "generic_device.json", "wb") as file:
        file.write(dumps([
        {"name": f"d{index}", "model": f"Model{randrange(1, 21)}"}
        for index in range(150_000)
    ]))

def generate_links():
    with open(PATH / "generic_link.json", "wb") as file:
        file.write(dumps([
            {"name": f"l{index}", "model": f"Model{randrange(1, 51)}"}
            for index in range(30_000)
        ]))

def generate_workflow_association_table():
    association_table = [
        [f"[Shared] s{i}", f"[Shared] w{j}"]
        for j in range(1, 2000)
        for i in range(j, j + 30)
    ]
    with open(PATH / "service_workflow_table.json", "wb") as file:
        file.write(dumps(association_table))

def generate_pools():
    pools = []
    for index in range(1, 1_001):
        # we associate each pool of index (1)xyyy to a range of
        # at most 3K devices in [max(0, xK - 1), min(9, xK + 1)]
        x = index // 100
        pools.append(
            {
                "name": f"Pool {index}",
                "device_name": f"d[{max(x - 1, 0)}-{min(x + 1, 9)}]\\d{{3}}",
                "device_name_match": "regex",
            }
        )
    for index in range(1_001, 5_001):
        pools.append(
            {
                "name": f"Pool {index}",
                "device_name": ".*",
                "device_name_match": "regex",
            }
        )
    with open(PATH / "pool.json", "wb") as file:
        file.write(dumps(pools))

def generate_users():
    users = [{"name": f"user{index}"} for index in range(1, 1_001)]
    with open(PATH / "user.json", "wb") as file:
        file.write(dumps(users))

def generate_tasks():
    tasks = [{"name": f"task{index}"} for index in range(1, 2_001)]
    with open(PATH / "task.json", "wb") as file:
        file.write(dumps(tasks))

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
