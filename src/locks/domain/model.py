class Lock:
    def __init__(self, name: str, is_locked: bool):
        self.name = name

        self.is_locked = is_locked

    @property
    def is_acquired(self) -> bool:
        return self.is_locked

    def acquire(self):
        self.is_locked = True

    def release(self):
        self.is_locked = False
