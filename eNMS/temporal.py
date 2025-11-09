from datetime import timedelta
from temporalio import activity, workflow

from eNMS.controller import Controller


@activity.defn
async def temporal_job(service_id, kwargs):
    return Controller.run(service_id, **kwargs)


@workflow.defn(sandboxed=False)
class TemporalWorkflow:
    @workflow.run
    async def run(self, service_id, payload=None):
        return await workflow.execute_activity(
            temporal_job,
            args=[service_id, payload],
            start_to_close_timeout=timedelta(hours=1),
        )
