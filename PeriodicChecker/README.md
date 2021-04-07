# PeriodicChecker
Provide a common approach to task management.  
Task could be persistent or one-shoot depends on the calling parameters.  
## Run
The settings for connection within the underlying services should be provided at the `.env.prod`.  
The same file would be used for the docker container.  
The `run_server.sh` script would try to load the settings 
from the file and launch the API within the gunicorn on `localhost:8080`.  

Use `docker-compose up -d` for running the service within the nginx.
## API
The API has the following methods:
### ```POST /add_task``` - add the task to the running loop
The request's body should contain the fields: 
* `name:str(required)` - the name of the task
* `url:URL(required)` - the URL of the website that a task should process
* `register:bool(required)` - store the task at the persistent storage or not
* `run:bool` - the service should run the task right after the request
* `command_type:str` - will be `fetch` if not provided. Any other types not implemented yet.   
The field will be using by the broker as a topic name.  
* `params:dict` - additional parameters for the task:
    * `repeat:int` - how many times the task should be executed.   
    The `Task` will be executed forever if not provided.  
    Please note that with `run:true` the `Task` will be launched `repeat+1` times.
    * `retry:int` - retry on error count. The system will try to re-execute the task if an error acquired.
    * `sleep_time:int` - task will be delayed.
    * `send_to:str` - the channel name that would be using by a broker to send the results.
    * `regex:str` - the pattern that should be used for regex search in the response's body.
#### Request example 
```json
{
  "name": "task_name",
  "url": "localhost:8080",
  "register": true,
  "run": true,
  "command_type": "fetch",
  "params": {
    "regex": ".*submit.*",
    "repeat": 2,
    "send_to": "fetch",
    "retry": 3
  }
}
```
## TaskFactory
The `TaskDispatcher` object will create the `Task` rely on the parameters provided by a request.  
You could implement any different task's types with the `task.py`.   
Make sure the new one is implement the `TaskInterface` (see below).  
Every `Task` should be registered in the `tasks.task_dict`.  
The `TaskDispatcher` will use this dict when creating the `Task` object based on the `command_type` field.
## Task
If the `register` parameter set to `true` a persistent task would be stored in the sqlite database.  
The `TaskRunner` object will load and execute the persistent tasks every time the app will be relaunched.  
A one-shoot task will be executed right after calling from API and would not be re-execute in the future.   
The `Task` object should implement the following interface:
```python
class TaskInterface(ABC):
    __slots__ = "name", "url", "task_id", "regex", "command_type", "repeat", "retry", "sleep_time", "status"

    @abstractmethod
    async def run(self, results: Awaitable): ...
```
Where the `run()` should return the unique id of the task in the `results` queue as a key.  
It will be used for the task management process.    
Could raise `errors.task_errors.TaskError`.
### Task result message example
```json
{
  "uuid_task_id": {
      "message": "some_string"
  }
}
```
## Broker
The `Broker` object is responsible for sending the results to the channel based on the `send_to` task parameter.   
The `task_id` will be passed to the broker's `send` method as a parameter.   
Could raise `errors.broker_errors.BrokerErrors`.
