from asyncio import run
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


@workflow.defn
class SignalWorkflow:
    def __init__(self):
        self.approved = False
    
    @workflow.signal
    async def approve(self):
        self.approved = True
    
    @workflow.run
    async def run(self):
        workflow.logger.info("Before Wait Condition")
        await workflow.wait_condition(lambda: self.approved, timeout=timedelta(hours=1))
        workflow.logger.info("After Wait Condition")
        return "Workflow Completed"

async def main():
    client = await Client.connect("localhost:7233")
    await Worker(
        client,
        task_queue="signal-queue",
        workflows=[SignalWorkflow],
    ).run()


async def approve_order(workflow_id: str):
    client = await Client.connect("localhost:7233")
    await client.get_workflow_handle(workflow_id).signal("approve")

if __name__ == "__main__":
    run(main())
