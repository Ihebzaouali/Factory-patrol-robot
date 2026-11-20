class PACSProfile:
    def __init__(
            self,
            rows: int,
            columns: int
            ) -> None:
        self.rows = rows
        self.columns = columns


class IndexingProfile:
    def __init__(
            self,
            camera: int = 0,
            gps: int = 0,
            imu: int = 0,
            lidar2d: int = 0,
            lidar3d: int = 0,
            ins: int = 0,
            ) -> None:
        self.camera = camera
        self.gps = gps
        self.imu = imu
        self.lidar2d = lidar2d
        self.lidar3d = lidar3d
        self.ins = ins


# Platform
# - all supported platforms
class Platform:
    # Dingo D V1
    DD100 = 'dd100'
    # Dingo O V1
    DO100 = 'do100'
    # Dingo D V1.5
    DD150 = 'dd150'
    # Dingo D V1.5
    DO150 = 'do150'
    # Jackal V1
    J100 = 'j100'
    # Husky V2
    A200 = 'a200'
    # Husky V3
    Rallp = 'rallp'
    # Ridgeback V1
    R100 = 'r100'
    # Warthog V2
    W200 = 'w200'
    # Genric Robot
    GENERIC = 'generic'

    ALL = [
        DD100,
        DO100,
        DD150,
        DO150,
        J100,
        A200,
        Rallp,
        R100,
        W200,
        GENERIC
    ]

    PACS = {
        GENERIC: PACSProfile(rows=100, columns=100),
        A200: PACSProfile(rows=8, columns=7),
        Rallp: PACSProfile(rows=9, columns=5),
        J100: PACSProfile(rows=4, columns=2),
        W200: PACSProfile(rows=100, columns=100),
        R100: PACSProfile(rows=100, columns=100),
    }

    INDEX = {
        GENERIC: IndexingProfile(),
        A200: IndexingProfile(),
        Rallp: IndexingProfile(),
        DD100: IndexingProfile(imu=1),
        DO100: IndexingProfile(imu=1),
        DD150: IndexingProfile(imu=1),
        DO150: IndexingProfile(imu=1),
        J100: IndexingProfile(gps=1, imu=1),
        R100: IndexingProfile(imu=1),
        W200: IndexingProfile(imu=1),
    }

    @staticmethod
    def assert_is_supported(platform):
        """
        Raise an exception if the platform is not presently supported/usable.

        Unsupported platforms may become supported in a future release, and there are no plans
        to remove it; it simply is not (yet) compatible with the current ROS release.

        @param platform  The platform-identifying serial number prefix (e.g. 'a200', 'j100')

        @exception UnsupportedPlatformException if the platform is not supported
        """
        # currently all platforms are supported, nothing to do
        pass

    @staticmethod
    def notify_if_deprecated(platform):
        """
        Print a notification that the selected platform is deprecated.

        Deprecated platforms may have their support removed in a future version

        @param platform  The platform-identifying serial number prefix (e.g. 'a200', 'j100')
        """
        # currently nothing is deprecated, so nothing to do here (yet)
        pass
