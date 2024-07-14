import dataclasses
import datetime


@dataclasses.dataclass
class ScannedCompute:
    cpu_count: int
    memory_size: int
    cgroups_supported: bool
    version: str
    images: list
    os_type: str
    environment: str
    display_name: str
    command_line: str
    ip_addresses: [str]
    domain_name: str
    uptime: int
    architecture: str
    launch_time: datetime.datetime
