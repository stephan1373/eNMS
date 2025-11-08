from asyncio import run
from datetime import timedelta

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def say_hello(name):
    return f"Hi {name}!"

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name):
        result = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
        print(f"Workflow result: {result}")
        return result

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow],
        activities=[say_hello],
    )
    await worker.run()

if __name__ == "__main__":
    run(main())
