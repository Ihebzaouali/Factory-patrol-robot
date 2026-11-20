class DomainID:

    def __init__(self, _id: int = 0) -> None:
        self.assert_valid(_id)
        self.id = _id

    def __int__(self) -> int:
        return self.id

    @staticmethod
    def is_valid(_id: int) -> bool:
        # Check Type
        if not isinstance(_id, int):
            return False
        # 0-101 Range
        if not (0 <= _id <= 101):
            return False
        return True

    @staticmethod
    def assert_valid(_id: int) -> None:
        # Check Type
        assert isinstance(_id, int), (
            'Domain ID must be an integer'
        )
        # 0 - 101 Range
        assert 0 <= _id <= 101, (
            'Domain ID must be in range 0 - 101'
        )
        return
