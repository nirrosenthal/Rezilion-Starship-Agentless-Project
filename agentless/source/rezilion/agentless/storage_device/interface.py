
class StorageDeviceInterface:
    def __init__(self, _id: str, scanned_compute_id: str, is_root_device: bool = False):
        self._id = _id
        self._scanned_compute_id = scanned_compute_id
        self._is_root_device = is_root_device

    @property
    def id(self) -> str:
        return self._id

    @property
    def is_root_device(self) -> bool:
        return self._is_root_device

    @property
    def mounted_device_path_on_host(self) -> str:
        raise NotImplementedError()

    @property
    def device_path_on_scanned_compute(self) -> str:
        raise NotImplementedError()

    def mount(self, path_to_mount: str):
        raise NotImplementedError()

    def teardown(self):
        raise NotImplementedError()

    @staticmethod
    def supported(_id: str) -> bool:
        raise NotImplementedError()

    @property
    def storage_mount_location_on_host(self):
        raise NotImplementedError()

