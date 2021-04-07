class ProcessingException(BaseException): ...


class ProcessingError(ProcessingException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)
