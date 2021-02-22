class GrapeVineMessageException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GrapeVineClientDisconnectedException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GrapeVineMessageFormatException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GrapeVineQueueException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GrapeVineIdentifierNotFound(Exception):
    def __init__(self, msg):
        super().__init__(msg)
