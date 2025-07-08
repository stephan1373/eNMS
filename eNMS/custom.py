from itertools import batched
from re import sub
from ruamel.yaml import YAML
from uuid import uuid4
from warnings import warn

try:
    from ldap3 import Connection
except ImportError as exc:
    warn(f"Couldn't import ldap3 module({exc})")

from eNMS.database import db
from eNMS.environment import env
from eNMS.variables import vs


class CustomApp(vs.TimingMixin):
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
        return

    def runner_global_variables(self, run):
        return {}

    def server_template_context(self):
        return {}

    def create_fake_logs(self):
        entry = ("changelog", "content", "admin", vs.get_time())
        query = "INSERT INTO changelog (type, content, author, time) VALUES (?, ?, ?, ?)"
        batch_size = vs.database["transactions"]["batch_size"]
        log_size = vs.settings["on_startup"]["create_fake_logs"]
        with env.timer("Create Fake Changelogs"):
            changelogs = (entry for _ in range(log_size))
            cursor = db.session.connection().connection.cursor()
            for batch in batched(changelogs, batch_size):
                cursor.executemany(query, batch)
            db.session.commit()

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
