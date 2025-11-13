from asyncio import run as asyncio_run
from sqlalchemy import ForeignKey, Integer
from warnings import warn
from wtforms.validators import InputRequired

try:
    from temporalio.client import Client
except ImportError as exc:
    warn(f"Couldn't import temporalio.client module ({exc})")

from eNMS.database import db
from eNMS.fields import HiddenField, StringField
from eNMS.forms import ServiceForm
from eNMS.models.automation import Service
from eNMS.variables import vs


class SendTemporalSignalService(Service):
    __tablename__ = "send_temporal_signal_service"
    pretty_name = "Temporal Send Signal"
    id = db.Column(Integer, ForeignKey("service.id"), primary_key=True)
    server_url = db.Column(db.SmallString)
    workflow_id = db.Column(db.SmallString)
    run_id = db.Column(db.SmallString)
    signal_name = db.Column(db.SmallString)
    signal_args = db.Column(db.LargeString)

    __mapper_args__ = {"polymorphic_identity": "send_temporal_signal_service"}

    def job(self, run, device=None):
        local_variables = locals()
        kwargs = {
            "url": run.sub(run.server_url, local_variables),
            "workflow_id": run.sub(run.workflow_id, local_variables),
            "run_id": run.sub(run.run_id, local_variables),
            "signal_name": run.sub(run.signal_name, local_variables),
            "signal_args": run.eval(run.signal_args, **local_variables)[0],
        }
        run.log("info", f"Sending Temporal signal (kwargs: '{kwargs}')", device)
        if run.dry_run:
            return kwargs

        async def send_signal():
            client = await Client.connect(kwargs["url"])
            run_kw = {"run_id": kwargs["run_id"]} if kwargs["run_id"] else {}
            handle = client.get_workflow_handle(kwargs["workflow_id"], **run_kw)
            await handle.signal(kwargs["signal_name"], *kwargs["signal_args"])
            return {"success": True, "kwargs": kwargs, "result": "Signal sent"}

        return asyncio_run(send_signal())


class SendTemporalSignalForm(ServiceForm):
    form_type = HiddenField(default="send_temporal_signal_service")
    server_url = StringField(
        "Temporal Server URL",
        [InputRequired()],
        default=vs.settings["temporal"]["url"],
        substitution=True,
    )
    workflow_id = StringField("Workflow ID", [InputRequired()], substitution=True)
    run_id = StringField("Run ID (Optional)", substitution=True)
    signal_name = StringField("Signal Name", [InputRequired()], substitution=True)
    signal_args = StringField("Signal Value", python=True)
