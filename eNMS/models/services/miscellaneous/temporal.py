from asyncio import run as asyncio_run
from datetime import timedelta
from sqlalchemy import Boolean, ForeignKey, Integer
from warnings import warn

from uuid import uuid4
from wtforms.validators import InputRequired

try:
    from temporalio.client import Client
except ImportError as exc:
    warn(f"Couldn't import temporalio.client Client module ({exc})")

from eNMS.database import db
from eNMS.fields import (
    BooleanField,
    HiddenField,
    IntegerField,
    StringField,
)
from eNMS.forms import ServiceForm
from eNMS.models.automation import Service
from eNMS.variables import vs


class TemporalService(Service):
    __tablename__ = "temporal_service"
    pretty_name = "Temporal Workflow"
    id = db.Column(Integer, ForeignKey("service.id"), primary_key=True)
    server_url = db.Column(db.SmallString)
    workflow_name = db.Column(db.SmallString)
    task_queue = db.Column(db.SmallString)
    workflow_args = db.Column(db.LargeString)
    timeout_seconds = db.Column(Integer, default=3600)
    wait_for_result = db.Column(Boolean, default=True)

    __mapper_args__ = {"polymorphic_identity": "temporal_service"}

    @staticmethod
    def job(self, run, device=None):
        local_variables = locals()
        url = run.sub(run.server_url, local_variables)
        workflow_name = run.sub(run.workflow_name, local_variables)
        workflow_id = f"{workflow_name}-{uuid4()}"
        kwargs = {
            "id": workflow_id,
            "args": run.eval(run.workflow_args, **local_variables)[0],
            "task_queue": run.sub(run.task_queue, local_variables),
        }
        run.log("info", f"Starting Temporal workflow: {workflow_name}", device)
        if run.dry_run:
            return {"url": url, "workflow_name": workflow_name, **kwargs}
        kwargs["execution_timeout"] = timedelta(seconds=self.timeout_seconds)
        async def trigger_workflow():
            client = await Client.connect(url)
            method = "execute_workflow" if self.wait_for_result else "start_workflow"
            result = await getattr(client, method)(workflow_name, **kwargs)
            status = "Completed" if self.wait_for_result else "Started (async)"
            return {"workflow_id": workflow_id, "status": status, "result": result}
        run.log("info", f"Starting Workflow ID: {workflow_id}", device)
        return asyncio_run(trigger_workflow())


class TemporalForm(ServiceForm):
    form_type = HiddenField(default="temporal_service")
    server_url = StringField(
        "Temporal Server URL",
        [InputRequired()],
        default=vs.settings["temporal"]["url"],
        substitution=True,
    )
    workflow_name = StringField("Workflow Name", [InputRequired()], substitution=True)
    task_queue = StringField("Task Queue", [InputRequired()], substitution=True)
    workflow_args = StringField("Workflow Arguments", python=True)
    timeout_seconds = IntegerField("Timeout (seconds)", default=3600)
    wait_for_result = BooleanField("Wait for Workflow Result", default=True)
