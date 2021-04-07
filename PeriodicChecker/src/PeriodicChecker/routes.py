import json
import logging
from asyncio import get_running_loop
from marshmallow import Schema, fields
from aiohttp.web import Request, HTTPAccepted, HTTPBadRequest, HTTPInternalServerError, Response


class AddTaskSchema(Schema):
    url = fields.Url(required=True)
    name = fields.Str(required=True)
    register = fields.Boolean(required=True)
    run = fields.Boolean()
    command_type = fields.Str()
    params = fields.Dict()


async def add_task(request: Request):
    """Provide the task to the main_loop"""
    schema = AddTaskSchema()
    try:
        req_data = await request.json()
        field_error = [(k, v) for k, v in schema.validate(req_data).items()]
        if field_error:
            return HTTPBadRequest(text=f"Request validation error: {field_error}")
        run = req_data.pop("run", None)
        call_params = req_data.pop("params", dict())
        task = await request.app["task_dispatcher"].create_task(**req_data, **call_params)
        if run:
            job = get_running_loop().create_task(request.app["task_runner"].run_task(task))
            job.set_name(task.task_id)

    except json.decoder.JSONDecodeError:
        return HTTPBadRequest()
    except ValueError as e:
        return HTTPBadRequest(text=e.__str__())
    except Exception as e:
        logging.getLogger(__name__).error(e)
        return HTTPInternalServerError()
    return HTTPAccepted()


async def task_list(request):
    """Get list of the active tasks"""
    return Response(status=418, text="may be short and stout")


async def status(request):
    """Get current status of all tasks"""
    return Response(status=418, text="may be short and stout")
