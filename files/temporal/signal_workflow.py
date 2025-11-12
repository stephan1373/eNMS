from asyncio import run
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


@workflow.defn
class SignalWorkflow:
    def __init__(self):
        self.value = None
    
    @workflow.signal
    async def set_value(self, new_value):
        self.value = new_value
    
    @workflow.run
    async def run(self):
        workflow.logger.info("Waiting for value...")
        await workflow.wait_condition(lambda: self.value is not None, timeout=timedelta(hours=1))
        workflow.logger.info(f"Received value: {self.value}")
        return f"Workflow completed with value: {self.value}"

async def main():
    client = await Client.connect("localhost:7233")
    await Worker(client, task_queue="signal-queue", workflows=[SignalWorkflow]).run()

async def send_signal(workflow_id: str, value):
    client = await Client.connect("localhost:7233")
    await client.get_workflow_handle(workflow_id).signal("set_value", value)

if __name__ == "__main__":
    run(main())
