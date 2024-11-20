from re import sub
from ruamel.yaml import YAML
from uuid import uuid4
from warnings import warn

try:
    from ldap3 import Connection
except ImportError as exc:
    warn(f"Couldn't import ldap3 module({exc})")

from eNMS.environment import env
from eNMS.variables import vs


class CustomApp:
    def ldap_authentication(self, user, name, password):
        if not hasattr(env, "ldap_servers"):
            env.log("error", "LDAP authentication failed: no server configured")
            return False
        user = f"uid={name},dc=example,dc=com"
        success = Connection(env.ldap_servers, user=user, password=password).bind()
        return {"name": name, "is_admin": True} if success else False

    def tacacs_authentication(self, user, name, password):
        if not hasattr(env, "tacacs_client"):
            env.log("error", "TACACS+ authentication failed: no server configured")
            return False
        success = env.tacacs_client.authenticate(name, password).valid
        return {"name": name, "is_admin": True} if success else False

    def parse_configuration_property(self, device, property, value=None):
        if not value:
            value = getattr(device, property)
        if device.operating_system == "EOS" and property == "configuration":
            value = sub(r"(username.*secret) (.*)", "\g<1> ********", value)
        return value

    def generate_uuid(self):
        return str(uuid4())

    def log_post_processing(_self, **kwargs):
        return

    def run_post_processing(self, run, run_result):
        if run.is_main_run:
            env.log(
                "info",
                (
                    f"RUNTIME {run_result['runtime']} - USER {run.creator} -"
                    f"SERVICE '{run_result['properties']['scoped_name']}' - "
                    f"Completed in {run_result['duration']}"
                ),
            )

    def runner_global_variables(self):
        return {}

    def server_template_context(self):
        return {}

    def get_yaml_instance(self):
        yaml = YAML(typ="safe")
        yaml.default_style = '"'

        def representer(dumper, data):
            style = "|" if "\n" in data else None
            data = data.lstrip()
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)

        def tuple_constructor(loader, node):
            return tuple(loader.construct_sequence(node))

        yaml.constructor.add_constructor(
            "tag:yaml.org,2002:python/tuple", tuple_constructor
        )
        yaml.representer.add_representer(str, representer)
        yaml.representer.ignore_aliases = lambda *args: True
        return yaml


vs.custom = CustomApp()
