async def test_add_task(api_cli):
    resp = await api_cli.post(
        '/add_task', json={
            "name": "name",
            "url": "http://ya.ru",
            "run": False,
            "register": False,
        }
    )
    assert resp.status == 202


async def test_add_task_no_params(api_cli):
    resp = await api_cli.post(
        '/add_task'
    )
    assert resp.status == 400


async def test_add_task_schema(api_cli):
    resp = await api_cli.post(
        '/add_task', json={
            "name": "name",
            "run": False,
            "register": False,
        }
    )
    assert resp.status == 400
