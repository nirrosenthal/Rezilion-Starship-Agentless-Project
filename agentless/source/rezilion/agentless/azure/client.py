from azure.mgmt.compute import ComputeManagementClient
from rezilion.agentless.azure.api import AzureApi
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from rezilion.agentless.azure.exceptions import AzureOperationError
from typing import Union
from azure.core.polling._poller import LROPoller
from azure.mgmt.compute.models import Disk, Snapshot, VirtualMachine

SUCCESSFULL_OPERATION_STATUS = "succeeded"

class AzureClient(AzureApi):

    def __init__(self, client_type: str, **kwargs):
        if client_type == 'secrets':
            self._client = SecretClient(credential=DefaultAzureCredential(), **kwargs)
        else:
            self._client = ComputeManagementClient(DefaultAzureCredential(), self.subscription_id).__getattribute__(client_type)

    def __getattr__(self, item):
        if hasattr(AzureApi, item):
            return super().__getattribute__(item)

        return self._client.__getattribute__(item)

    def update_resource(self, resource_name: str, resource: Union[Disk, Snapshot, VirtualMachine, dict]) -> LROPoller:
        try:
            poller = self._client.begin_create_or_update(AzureApi().resource_group_name, resource_name, resource)
            poller.wait()
            if poller.status().lower() != SUCCESSFULL_OPERATION_STATUS:
                print(f"Exception with poller status {poller.status()} with resource {resource_name}")
                raise AzureOperationError
        except Exception as e:
            print(f"Exception while updating resource {resource_name}: {str(e)}")
            raise AzureOperationError
        return poller

    def delete_resource(self, resource_name: str):
        try:
            poller = self._client.begin_delete(AzureApi().resource_group_name, resource_name)
            poller.wait()
            if poller.status().lower() != SUCCESSFULL_OPERATION_STATUS:
                print(f"Exception with poller status {poller.status()} with resource {resource_name}")
                raise AzureOperationError
        except Exception as e:
            print(f"Exception while updating resource {resource_name}: {str(e)}")
            raise AzureOperationError
