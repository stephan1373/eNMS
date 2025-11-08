from asyncio import CancelledError, run, sleep
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker


@workflow.defn
class SleepWorkflow:
    @workflow.run
    async def run(self, sleep_seconds: int) -> str:
        print(f"Run started (sleeping {sleep_seconds} seconds)")
        workflow.logger.info(f"Starting sleep for {sleep_seconds} seconds")
        try:
            await sleep(sleep_seconds)
            workflow.logger.info("Sleep completed successfully")
            return f"Slept for {sleep_seconds} seconds"
        except CancelledError:
            workflow.logger.info("Workflow was cancelled during sleep")
            return "Workflow cancelled"

async def main():
    client = await Client.connect("localhost:7233")
    await Worker(client, task_queue="sleep-task-queue", workflows=[SleepWorkflow]).run()


if __name__ == "__main__":
    run(main())
