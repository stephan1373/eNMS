from asyncio import run as asyncio_run, wait_for
from sqlalchemy import ForeignKey, Integer
from warnings import warn
from wtforms.validators import InputRequired

try:
    from temporalio.client import Client
except ImportError as exc:
    warn(f"Couldn't import temporalio.client module ({exc})")

from eNMS.database import db
from eNMS.fields import HiddenField, SelectField, StringField
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
    action = db.Column(db.SmallString)
    timeout_seconds = db.Column(Integer)

    __mapper_args__ = {"polymorphic_identity": "get_temporal_data_service"}

    def job(self, run, device=None):
        local_variables = locals()
        url = run.sub(run.server_url, local_variables)
        workflow_id = run.sub(run.workflow_id, local_variables)
        run_id = run.sub(run.run_id, local_variables)
        workflow_data = {"url": url, "workflow_id": workflow_id, "run_id": run_id}
        run.log("info", f"Getting data for Temporal workflow '{workflow_id}'", device)
        if run.dry_run:
            return {"action": run.action, **workflow_data}

        async def get_workflow_info():
            client = await Client.connect(url)
            kwargs = {"run_id": run_id} if run_id else {}
            handle = client.get_workflow_handle(workflow_id, **kwargs)
            if run.action == "describe":
                description = await handle.describe()
                return {
                    "result": {
                        "workflow_id": description.workflow_id,
                        "run_id": description.run_id,
                        "status": description.status.name,
                        "start_time": description.start_time,
                        "execution_time": description.execution_time,
                        "close_time": description.close_time,
                        "workflow_type": description.workflow_type,
                    },
                    **workflow_data
                }
            else:
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
    action = SelectField(
        "Action",
        choices=[
            ("describe", "Describe (Get Status)"),
            ("get_result", "Get Result (Wait for Completion)")
        ],
    )
    timeout_seconds = StringField("Timeout in Seconds (Optional)", substitution=True)
