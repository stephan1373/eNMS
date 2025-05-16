from orjson import dumps
from pathlib import Path
from random import randrange

PATH = (
    Path.cwd().parent.parent.parent
    / "eNMS-prod"
    / "files"
    / "migrations"
    / "model_scalability"
)

def generate_services():
    services = [
        {
            "name": f"[Shared] s{index}",
            "scoped_name": f"s{index}",
            "shared": True,
            "type": "netmiko_commands_service",
        }
        for index in range(1, 10000)
    ]
    with open(PATH / "service.json", "wb") as migration_file:
        migration_file.write(dumps(services))
    services = [
        {
            "name": f"[Shared] w{index}",
            "scoped_name": f"w{index}",
            "shared": True,
            "type": "workflow",
        }
        for index in range(1, 2000)
    ]
    with open(PATH / "service.json", "wb") as migration_file:
        migration_file.write(dumps(services))


def generate_workflow_association_table():
    services.extend(
        [
            {
                "name": f"w{index}",
                "scoped_name": f"w{index}",
                "type": "workflow",
                "services": list(
                    set(f"[Shared] s{randrange(1, 30)}" for _ in range(3))
                ),
            }
            for index in range(1, 5)
        ]
    )

def generate_devices():
    devices = [{"name": f"d{index}"} for index in range(1, 80_001)]
    with open(PATH / "generic_device.json", "wb") as migration_file:
        migration_file.write(dumps(devices))

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
    with open(PATH / "pool.json", "wb") as migration_file:
        migration_file.write(dumps(pools))

def generate_users():
    users = [{"name": f"user{index}"} for index in range(1, 1_001)]
    with open(PATH / "user.json", "wb") as migration_file:
        migration_file.write(dumps(users))

def generate_tasks():
    tasks = [{"name": f"task{index}"} for index in range(1, 2_001)]
    with open(PATH / "task.json", "wb") as migration_file:
        migration_file.write(dumps(tasks))

def generate_networks():
    networks = [
        {
            "name": f"w{index}",
            "devices": list(set(f"d{randrange(1, 80_000)}" for _ in range(30))),
        }
        for index in range(1, 1_001)
    ]
    with open(PATH / "network.json", "wb") as migration_file:
        migration_file.write(dumps(networks))
