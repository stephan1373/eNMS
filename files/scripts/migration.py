from collections import defaultdict
from json import dumps
from orjson import dumps as or_dumps, loads as or_loads, OPT_INDENT_2, OPT_SORT_KEYS
from pathlib import Path
from ruamel.yaml import YAML


FILENAME = "examples"
PATH = Path.cwd().parent.parent.parent / "eNMS-prod2" / "files" / "migrations"


def get_yaml_instance():
    yaml = YAML()
    yaml.default_style = '"'

    def representer(dumper, data):
        style = "|" if "\n" in data else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)

    yaml.representer.add_representer(str, representer)
    yaml.representer.ignore_aliases = lambda *args: True
    return yaml


def migrate_from_4_to_4_2():
    with open(PATH / FILENAME / "service.yaml", "r") as migration_file:
        services = yaml.load(migration_file)
    for service in services:
        service["priority"] += 9
        if service["type"] == "rest_call_service":
            service["custom_username"] = service.pop("username", "")
            service["custom_password"] = service.pop("password", "")
        if service["type"] == "git_service":
            actions = []
            if "git_repository" in service:
                service["local_repository"] = service.pop("git_repository")
            for action in ("add_commit", "pull", "push"):
                if service.pop(action, False):
                    actions.append(action)
            service["actions"] = actions
    with open(PATH / FILENAME / "service.yaml", "w") as migration_file:
        yaml.dump(services, migration_file)


def migrate_from_4_2_to_4_3():
    with open(PATH / FILENAME / "service.yaml", "r") as migration_file:
        services = yaml.load(migration_file)
    for service in services:
        if service["type"] == "netmiko_validation_service":
            service["type"] = "netmiko_commands_service"
            service["commands"] = service.pop("command", "")
        if service["type"] == "data_extraction_service":
            service["type"] = "data_processing_service"
        if service.pop("use_device_driver", False):
            service["driver"] = "device"
    with open(PATH / FILENAME / "service.yaml", "w") as migration_file:
        yaml.dump(services, migration_file)


def migrate_from_4_3_to_4_4():
    with open(PATH / FILENAME / "credential.yaml", "r") as credential_file:
        credentials = yaml.load(credential_file)
    for credential in credentials:
        credential["groups"] = credential.pop("user_pools")
    with open(PATH / FILENAME / "credential.yaml", "w") as credential_file:
        yaml.dump(credentials, credential_file)


def migrate_5_1_to_5_2():
    positions = defaultdict(dict)
    yaml = get_yaml_instance()
    with open(PATH / FILENAME / "service.yaml", "r") as service_file:
        services = yaml.load(service_file)
    for service in services:
        for workflow_name, coords in service["positions"].items():
            positions[workflow_name][service["name"]] = coords
    for service in services:
        service.pop("positions")
        if service["type"] == "workflow" and service["name"] in positions:
            service["positions"] = positions[service["name"]]
    with open(PATH / FILENAME / "service.yaml", "w") as service_file:
        yaml.dump(services, service_file)
    positions = defaultdict(dict)
    with open(PATH / FILENAME / "device.yaml", "r") as device_file:
        devices = yaml.load(device_file)
    for device in devices:
        for network_name, coords in device["positions"].items():
            positions[network_name][device["name"]] = coords
    for device in devices:
        device.pop("positions")
        if device["type"] == "network" and device["name"] in positions:
            device["positions"] = positions[device["name"]]
    with open(PATH / FILENAME / "device.yaml", "w") as device_file:
        yaml.dump(devices, device_file)
    with open(PATH / FILENAME / "credential.yaml", "r") as credential_file:
        credentials = yaml.load(credential_file)
    for credential in credentials:
        credential["rbac_use"] = credential.pop("groups")
    with open(PATH / FILENAME / "credential.yaml", "w") as credential_file:
        yaml.dump(credentials, credential_file)
    with open(PATH / FILENAME / "secret.yaml", "r") as service_file:
        secrets = yaml.load(service_file)
    data = [
        {
            "admin_only": "false",
            "creator": "admin",
            "data_type": "secret",
            "name": ">Secrets",
            "path": "/Secrets",
            "scoped_name": "Secrets",
            "type": "store",
        }
    ]
    for secret in secrets:
        name = secret["name"]
        secret["name"] = f">Secrets>{name}"
        secret["path"] = f"/Secrets/{name}"
        secret["scoped_name"] = name
        secret["store"] = ">Secrets"
        data.append(secret)
    with open(PATH / FILENAME / "data.yaml", "w") as data_file:
        yaml.dump(data, data_file)


def migrate_5_2_to_5_3():
    yaml = get_yaml_instance()
    with open(PATH / FILENAME / "device.yaml", "r") as device_file:
        devices = yaml.load(device_file)
    for device in devices:
        if device["type"] == "device":
            device["type"] = "generic_device"
    with open(PATH / FILENAME / "device.yaml", "w") as device_file:
        yaml.dump(devices, device_file)
    with open(PATH / FILENAME / "link.yaml", "r") as link_file:
        links = yaml.load(link_file)
    for link in links:
        if link["type"] == "link":
            link["type"] = "generic_link"
    with open(PATH / FILENAME / "link.yaml", "w") as link_file:
        yaml.dump(links, link_file)
    with open(PATH / FILENAME / "file.yaml", "r") as file_file:
        files = yaml.load(file_file)
    for file in files:
        if file["type"] == "file":
            file["type"] = "generic_file"
    with open(PATH / FILENAME / "file.yaml", "w") as file_file:
        yaml.dump(files, file_file)
    with open(PATH / FILENAME / "service.yaml", "r") as service_file:
        services = yaml.load(service_file)
    for service in services:
        if service["type"] != "rest_call_service":
            continue
        service["payload"] = dumps(service["payload"])
    with open(PATH / FILENAME / "service.yaml", "w") as service_file:
        yaml.dump(services, service_file)


def migrate_5_2_to_5_3_json():
    with open(PATH / FILENAME / "rest_call_service.json", "rb") as service_file:
        services = or_loads(service_file.read())
    for service in services:
        service["payload"] = dumps(service["payload"])
    with open(PATH / FILENAME / "rest_call_service.json", "wb") as service_file:
        service_file.write(
            orjson.dumps(
                services,
                option=OPT_INDENT_2 | OPT_SORT_KEYS
            )
        )


migrate_5_2_to_5_3_json()
