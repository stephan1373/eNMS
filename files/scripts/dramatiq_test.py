# To test dramatiq:
# - Start the workers with "dramatiq dramatiq_test -p 2 -t 4"
# - Send the tasks with "python dramatiq_test.py"

from dramatiq import actor, get_broker
from dramatiq.middleware import ProcessReloader

from time import sleep


broker = get_broker()
broker.add_middleware(ProcessReloader(reload_counter=10))


@actor
def example(index):
    sleep(0.1)

@actor
def example2(index):
    sleep(0.1)

if __name__ == "__main__":
    for index in range(10):
        example.send(index)
    for index in range(10):
        example2.send(index)
