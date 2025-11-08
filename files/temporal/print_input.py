from asyncio import run
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def print_input(name):
    return f"Hi {name}!"

@workflow.defn
class PrintInput:
    @workflow.run
    async def run(self, name):
        result = await workflow.execute_activity(
            print_input,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
        print(f"Workflow result: {result}")
        return result

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="print-input-queue",
        workflows=[PrintInput],
        activities=[print_input],
    )
    await worker.run()

if __name__ == "__main__":
    run(main())
