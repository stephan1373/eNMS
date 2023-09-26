from dramatiq import actor, get_broker, get_logger, Middleware
from os import getpid, getppid, kill
from signal import SIGHUP
from threading import Lock
from time import sleep


class MaxJobs(Middleware):
    def __init__(self, max_tasks=10):
        self.lock = Lock()
        self.kill_counter = max_tasks
        self.job_counter = 0
        self.signaled = False
        self.logger = get_logger("max_jobs.app", MaxJobs)

    def before_process_message(self, *_):
        with self.lock:
            self.job_counter += 1

    def after_process_message(self, *_, **__):
        with self.lock:
            self.job_counter -= 1
            self.kill_counter -= 1
            self.logger.info(
                f"Active Jobs: {self.job_counter} - "
                f"Kill Counter: {self.kill_counter}"
            )
            if self.job_counter <= 0 and self.kill_counter <= 0 and not self.signaled:
                self.logger.warning(f"Killing process {getpid()}")
                kill(getppid(), SIGHUP)
                self.signaled = True


broker = get_broker()
broker.add_middleware(MaxJobs())


@actor
def example(index):
    sleep(0.1)

@actor
def example2(index):
    sleep(0.1)

if __name__ == "__main__":
    for index in range(250):
        example.send(index)
    for index in range(250):
        example2.send(index)
