import datetime
import rezilion.agentless.constants as constants
from urllib.error import URLError
from rezilion.agentless.azure.api import AzureApi


def parse_timestamp(timestamp: str) -> datetime.datetime:
    return datetime.datetime.strptime(timestamp, constants.DATETIME_FORMAT)


def generate_timestamp() -> str:
    return datetime.datetime.now().strftime(constants.DATETIME_FORMAT)


def is_in_azure() -> bool:
    try:
        AzureApi().current_vm_id
        return True
    except URLError:
        return False
