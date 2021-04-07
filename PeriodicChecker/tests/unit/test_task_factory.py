from PeriodicChecker.tasks.tasks import TaskInterface


async def test_create_task(task_dispatcher):
    name, url = "some_name", "http://mail.ru"
    task = await task_dispatcher.create_task(name=name, url=url, register=True)
    tid = task.task_id
    assert name == task.name and url == task.url
    assert isinstance(task, TaskInterface)
    task_dict = await task_dispatcher.load_tasks()
    task = task_dict.get(tid)
    assert task.url == url and task.name == name
