from urllib.request import Request, urlopen

AZURE_API_VERSION = "2021-02-01"
AZURE_META_DATA_SERVER_URL = 'http://169.254.169.254/metadata/instance/compute/'
AZURE_RESOURCE_GROUP_NAME_URL = f'{AZURE_META_DATA_SERVER_URL}resourceGroupName?api-version={AZURE_API_VERSION}&format=text'
AZURE_SUBSCRIPTION_ID_URL = f'{AZURE_META_DATA_SERVER_URL}subscriptionId?api-version={AZURE_API_VERSION}&format=text'
AZURE_CURRENT_VM_ID_URL = f'{AZURE_META_DATA_SERVER_URL}vmId?api-version={AZURE_API_VERSION}&format=text'
AZURE_CURRENT_VM_NAME_URL = f'{AZURE_META_DATA_SERVER_URL}osProfile/computerName?api-version={AZURE_API_VERSION}&format=text'
AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS = 5


class AzureApi:
    @property
    def resource_group_name(self):
        request = Request(AZURE_RESOURCE_GROUP_NAME_URL, headers={'Metadata': 'true'})
        with urlopen(request, timeout=AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS) as response:
            return response.read().decode()

    @property
    def subscription_id(self):
        request = Request(AZURE_SUBSCRIPTION_ID_URL, headers={'Metadata': 'true'})
        with urlopen(request, timeout=AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS) as response:
            return response.read().decode()

    @property
    def current_vm_id(self):
        request = Request(AZURE_CURRENT_VM_ID_URL, headers={'Metadata': 'true'})
        with urlopen(request, timeout=AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS) as response:
            return response.read().decode()

    @property
    def current_vm_name(self):
        request = Request(AZURE_CURRENT_VM_NAME_URL, headers={'Metadata': 'true'})
        with urlopen(request, timeout=AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS) as response:
            return response.read().decode()
