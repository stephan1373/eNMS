from asyncio import run as asyncio_run
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


class TemporalStopWorkflowService(Service):
    __tablename__ = "stop_temporal_workflow_service"
    pretty_name = "Temporal Stop Workflow"
    id = db.Column(Integer, ForeignKey("service.id"), primary_key=True)
    server_url = db.Column(db.SmallString)
    workflow_id = db.Column(db.SmallString)
    run_id = db.Column(db.SmallString)
    stop_method = db.Column(db.SmallString)
    terminate_reason = db.Column(db.SmallString)
    
    __mapper_args__ = {"polymorphic_identity": "stop_temporal_workflow_service"}
    
    def job(self, run, device=None):
        local_variables = locals()
        url = run.sub(run.server_url, local_variables)
        result = {
            "workflow_id": run.sub(run.workflow_id, local_variables),
            "run_id": run.sub(run.run_id, local_variables),
            "terminate_reason": run.sub(run.terminate_reason, local_variables),
            "status": run.stop_method,
        }
        run.log("info", f"Stopping Temporal workflow: {result['workflow_id']}", device)
        if run.dry_run:
            return {"url": url, **result}

        async def stop_workflow():
            client = await Client.connect(url)
            kwargs = {"run_id": result["run_id"]} if result["run_id"] else {}
            handle = client.get_workflow_handle(result["workflow_id"], **kwargs)
            if run.stop_method == "cancel":
                await handle.cancel()
            else:
                await handle.terminate(reason=result["terminate_reason"])
            return result

        return asyncio_run(stop_workflow())


class TemporalStopWorkflowForm(ServiceForm):
    form_type = HiddenField(default="stop_temporal_workflow_service")
    server_url = StringField(
        "Temporal Server URL",
        [InputRequired()],
        default=vs.settings["temporal"]["url"],
        substitution=True,
    )
    workflow_id = StringField("Workflow ID", [InputRequired()], substitution=True)
    run_id = StringField("Run ID (Optional)", substitution=True)
    stop_method = SelectField(
        "Stop Method",
        choices=[("cancel", "Cancel (Graceful)"), ("terminate", "Terminate (Force)")],
    )
    terminate_reason = StringField("Terminate Reason (Optional)", substitution=True)
