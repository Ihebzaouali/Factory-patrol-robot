class Discovery:
    SIMPLE = 'simple'
    SERVER = 'server'

    # All supported discovery modes, currently only set up for FastDDS
    ALL_SUPPORTED = [SIMPLE, SERVER]

    # The discovery mode that the system will default to
    DEFAULT = SIMPLE

    def __init__(
            self,
            mode: str = DEFAULT
            ) -> None:
        self.assert_valid(mode)
        self.mode = mode

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.mode == other
        elif isinstance(other, Discovery):
            return self.mode == other.mode
        else:
            return False

    def __str__(self) -> str:
        return self.mode

    @classmethod
    def is_valid(cls, mode: str) -> bool:
        return mode in cls.ALL_SUPPORTED

    @classmethod
    def assert_valid(cls, mode: str) -> None:
        assert cls.is_valid(mode), ('\n'.join([
            f'Discovery mode "{mode}" not supported.'
            f'Discovery mode must be one of: "{cls.ALL_SUPPORTED}"'
        ]))
