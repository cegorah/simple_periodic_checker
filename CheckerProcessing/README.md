# CheckerProcessing
The `ProcessingService` is pretty simple.  
It handles the message from the broker based on the `KAFKA_CONSUMER_TOPICS` setting.  
It the message's field `pattern_search` set to `match` the message will be provided to the `Processor` object and stored 
at the `ProcessedResults` table.  
Othrwise it will be stored at the `RawResult` table.
## Run
The settings for connection within the underlying services should be provided at the `.env.prod`.  
The same file would be used for the docker container.   
The `run_server.sh` script would try to load the settings 
from the file and launch the python file as a stand-alone application.  

Use `docker-compose up -d` for running the service as a container.
## Processor
Will process the message based on the parameters.  
Should implement the following interface:
```python
class ProcessorInterface(ABC):
    __slots__ = "storage_name"

    def __init__(self): ...

    @abstractmethod
    async def process(self, params: Dict) -> Dict: ...

    @abstractmethod
    async def close(self): ...
```
## Repository
Database layer abstraction that supports `raw_result` query.  
When initialized create the following tables:
* `tasks` - for storing the task's information that would be received from the message.
* `process` - keeps the `Processor` id's
* `processedresult` - keeps the result of the `Processor` works
* `rawresult` - store the result if the message should not be processed 
## TaskRunner
The main_loop that manage the underlying systems, e.g `Broker`, `Repository`, `Processors`. 
# TODO
* More tests.
* More `Processors` and the different conditions for them.
