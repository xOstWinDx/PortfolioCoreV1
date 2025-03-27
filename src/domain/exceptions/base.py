class ConflictException(Exception):
    def __init__(self, msg: str = "Already exists") -> None:
        super().__init__(msg)
