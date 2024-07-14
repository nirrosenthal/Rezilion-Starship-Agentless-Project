import datetime


class ComputeInterface:

    @classmethod
    def find(cls, not_scanned_since: datetime.datetime):
        raise NotImplementedError()

    def storage_devices(self):
        raise NotImplementedError()

    @property
    def id(self):
        raise NotImplementedError()

    def last_scanned(self):
        raise NotImplementedError()

    def tag_scanned(self):
        raise NotImplementedError()

    def get_scanned_compute(self):
        raise NotImplementedError()
