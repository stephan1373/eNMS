from asyncio import run as asyncio_run, wait_for
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


class GetTemporalDataService(Service):
    __tablename__ = "get_temporal_data_service"
    pretty_name = "Temporal Get Data Workflow"
    id = db.Column(Integer, ForeignKey("service.id"), primary_key=True)
    server_url = db.Column(db.SmallString)
    workflow_id = db.Column(db.SmallString)
    run_id = db.Column(db.SmallString)

    __mapper_args__ = {"polymorphic_identity": "get_temporal_data_service"}

    def job(self, run, device=None):
        local_variables = locals()
        url = run.sub(run.server_url, local_variables)
        workflow_id = run.sub(run.workflow_id, local_variables)
        run_id = run.sub(run.run_id, local_variables)
        workflow_data = {"url": url, "workflow_id": workflow_id, "run_id": run_id}
        run.log("info", f"Getting data for Temporal workflow '{workflow_id}'", device)
        if run.dry_run:
            return workflow_data

        async def get_workflow_info():
            client = await Client.connect(url)
            kwargs = {"run_id": run_id} if run_id else {}
            handle = client.get_workflow_handle(workflow_id, **kwargs)
            result = await wait_for(handle.result(), timeout=run.timeout_seconds)
            return {"result": result, **workflow_data}

        return asyncio_run(get_workflow_info())


class GetTemporalDataForm(ServiceForm):
    form_type = HiddenField(default="get_temporal_data_service")
    server_url = StringField(
        "Temporal Server URL",
        [InputRequired()],
        default=vs.settings["temporal"]["url"],
        substitution=True,
    )
    workflow_id = StringField("Workflow ID", [InputRequired()], substitution=True)
    run_id = StringField("Run ID (Optional)", substitution=True)
