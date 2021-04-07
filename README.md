# TODO
* Pydantic
* Tests
* Endpoints
* Decorators

# Solution
There are two packages that could be launched separately.  
`PeriodicChecker` is using for creating the task and send a response to the second one.  
`CheckerProcessing` is getting the message from a broker and store it in a database.  
You should provide the correct settings with the `.env.prod` file for every system before the launch.  
Please find the `README` for each package in their paths.
# Environment settings
* `LOG_LEVEL` - one of ["INFO", "ERROR", "DEBUG", "WARNING"]. Using for `logging.basicConfig`.  
## Connection strings
* `KAFKA_CONNECTION`
* `POSTGRESQL_CONNECTION`
* `TASK_STORAGE` - a path to the sqlite file where the task will be stored. Using by `PeriodicChecker`.
## Kafka SSL connection options
* `KAFKA_CA_PATH` 
* `KAFKA_CERT_PATH` 
* `KAFKA_KEY_FILE` 
* `KAFKA_CERT_PASS` 
## Kafka consumer settings
Using by `ProcessingService`
* `KAFKA_CONSUMER_GROUP`
* `KAFKA_CONSUMER_TOPICS` - comma separated name of the topics

# Message Types
The systems will exchange the messages.  
The messages should have the `task_id` as a high level object and could contain any json-serializable data.
## Example
```json
{ 
  "53eb2d1a-a03d-475b-9168-98e24dad05b7": 
  {
    "name": "cool", 
    "timestamp": "02/15/21 - 16:43:17", 
    "status": 200, 
    "load_time": "0.5934", 
    "pattern_search": "match"
  }
}
```

# Future improvements
* Different types of the tasks like `post` or `delete`. Only `fetch` is implemented for now.
* Add `/remove_task`, `/status`, `/tasks` API endpoints.
* Replace the `PeriodicChecker.TaskDispatcher.storage_path` parameter 
with a storage object for more flexible approach to store the tasks.
* The task storage object could be shared between the workers for scalability purposes.  
The `PeriodicChecker` service should manage the task status, e.g. `active`, `error`, `done`.
* e2e tests

# Issues
Repeat and retry logic at the `PeriodicChecker.task_runner` is pretty messy and should be refactoring.  
