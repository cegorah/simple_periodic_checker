class BrokerErrors(BaseException): ...


class SendMessageError(BrokerErrors):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)
