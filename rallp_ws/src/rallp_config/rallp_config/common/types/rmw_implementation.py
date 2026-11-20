class RMWImplementation:
    CONNEXT = 'rmw_connext_cpp'
    CYCLONE_DDS = 'rmw_cyclonedds_cpp'
    FAST_RTPS = 'rmw_fastrtps_cpp'
    GURUM_DDS = 'rmw_gurumdds_cpp'
    ZENOH_DDS = 'rmw_zenoh_cpp'

    ALL_SUPPORTED = [FAST_RTPS, ZENOH_DDS]

    DEFAULT = FAST_RTPS

    def __init__(
            self,
            rmw: str = DEFAULT
            ) -> None:
        self.assert_valid(rmw)
        self.rmw = rmw

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.rmw == other
        elif isinstance(other, RMWImplementation):
            return self.rmw == other.rmw
        else:
            return False

    def __str__(self) -> str:
        return self.rmw

    @classmethod
    def is_valid(cls, rmw: str) -> bool:
        return rmw in cls.ALL_SUPPORTED

    @classmethod
    def assert_valid(cls, rmw: str) -> None:
        assert cls.is_valid(rmw), ('\n'.join([
            'RMW "%s" not supported.' % rmw,
            'RMW must be one of: "%s"' % cls.ALL_SUPPORTED
        ]))
