from rezilion.agentless.storage_device.interface import StorageDeviceInterface
from rezilion.agentless.azure.api import AzureApi
from rezilion.agentless.azure.client import AzureClient
import subprocess

NOT_SUPPORTED_AZURE_SKUS = []


class Disk(StorageDeviceInterface):
    def __init__(self, disk_id: str, scanned_compute_id: str = "", is_root_device: bool = False):
        self._original_disk = AzureClient('disks').get(resource_group_name=AzureApi().resource_group_name, disk_name=disk_id)
        self._vm = AzureClient('virtual_machines').get(resource_group_name=AzureApi().resource_group_name,vm_name=scanned_compute_id)
        self._snapshot = None
        self._disk_copy = None
        self._device_mount_path_on_host = None
        self._is_root_device = is_root_device

    @staticmethod
    def supported(disk_id: str) -> bool:
        disk = AzureClient("disks").get(AzureApi().resource_group_name, disk_id)
        return disk.sku.name.lower() not in NOT_SUPPORTED_AZURE_SKUS

    def teardown(self):
        self._unmount_disk()
        AzureClient('snapshots').delete_resource(self._snapshot.name)
        self._detach_disk_from_vm()
        AzureClient('disks').delete_resource(self._disk_copy.name)

    def _unmount_disk(self):
        subprocess.run(["sudo", "umount", self._device_mount_path_on_host], check=True)

    def _detach_disk_from_vm(self):
        current_vm = AzureClient('virtual_machines').get(AzureApi().resource_group_name, AzureApi().current_vm_name)
        for data_disk in current_vm.storage_profile.data_disks:
            if data_disk.managed_disk.id == self._disk_copy.id:
                current_vm.storage_profile.data_disks.remove(data_disk)
        AzureClient('virtual_machines').update_resource(current_vm.name, current_vm)

