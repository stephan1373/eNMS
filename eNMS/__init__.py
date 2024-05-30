from eNMS.controller import controller
from eNMS.custom import CustomApp  # noqa: F401
from eNMS.database import db
from eNMS.environment import env
from eNMS.forms import form_factory
from eNMS.runner import Runner
from eNMS.server import server
from eNMS.variables import vs


def initialize():
    server.register_plugins()
    first_init = db._initialize(env)
    if vs.custom.detect_cli():
        return
    env._initialize()
    form_factory._initialize()
    controller._initialize(first_init)
    vs.set_template_context()
    Runner._initialize()


initialize()
