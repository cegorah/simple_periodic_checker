from os.path import isfile
import pytest
import asyncio


async def test_run_task(task_runner):
    name, url = "some_name", "http://mail.ru"
    task_dispatcher = task_runner.task_factory
    task = await task_dispatcher.create_task(name=name, url=url, register=False, repeat=1, sleep_time=3,
                                             regex=".*html.*")
    await task_runner.run_task(task)
    res_dict = await task_runner.results.get()
    res = next(iter(res_dict.values()))
    assert res.get("name") == name


async def test_send_task(task_runner, broker):
    name, url = "some_name", "http://mail.ru"
    task_dispatcher = task_runner.task_factory
    task_runner.broker = broker
    task = await task_dispatcher.create_task(name=name, url=url, register=False, repeat=2, sleep_time=2,
                                             regex=".*submit.*")
    await task_runner.run_task(task)


@pytest.mark.skipif(not isfile("./tests/test_db.db"), reason="Should load the tasks from a database")
async def test_loaded_task(task_runner, broker):
    task_runner.broker = broker
    timeout = 5
    while True:
        try:
            timeout -= 1
            if not timeout:
                raise asyncio.TimeoutError("Can't get results from queue")
            res = task_runner.results.get_nowait()
            if res:
                break
        except asyncio.queues.QueueEmpty:
            await asyncio.sleep(2)
