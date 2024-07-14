import datetime
import azure.mgmt.compute.models
from rezilion.agentless.compute.interface import ComputeInterface
from rezilion.agentless.azure.client import AzureClient
from rezilion.agentless.azure.api import AzureApi
import rezilion.agentless.common as common_methods
from rezilion.agentless.azure.disk import Disk


class VirtualMachine(ComputeInterface):
    def __init__(self, vm_name: str):
        self._vm = AzureClient('virtual_machines').get(resource_group_name=AzureApi().resource_group_name, vm_name=vm_name)

    @property
    def id(self) -> str:
        return self._vm.name

    def tag_scanned(self):
        scan_tag = {'rezilion-scanned': common_methods.generate_timestamp()}
        if self._vm.tags is None:
            self._vm.tags = scan_tag
        else:
            self._vm.tags.update(scan_tag)
        self._update_vm()

    @classmethod
    def find(cls, not_scanned_since: datetime.datetime):
        vm_client = AzureClient('virtual_machines')
        for vm in vm_client.list(vm_client.resource_group_name):
            if cls._should_scan(vm, not_scanned_since):
                yield VirtualMachine(vm.name)

    def storage_devices(self) -> Disk:
        disks = [self._vm.storage_profile.os_disk]
        disks.extend(self._vm.storage_profile.data_disks)
        for disk in disks:
            if Disk.supported(disk.name):
                yield Disk(disk.name, self._vm.name, self._is_root_device(disk.name))

    def _update_vm(self):
        try:
            poller = AzureClient('virtual_machines').\
                begin_create_or_update(AzureApi().resource_group_name, self._vm.name, self._vm)
            poller.wait()
        except Exception as e:
            print(f"Exception while updating VM {self._vm.name}: {str(e)}")

    def _is_root_device(self, disk_name: str) -> bool:
        return disk_name == self._vm.storage_profile.os_disk.name

    @classmethod
    def _should_scan(cls, vm: azure.mgmt.compute.models.VirtualMachine, not_scanned_since: datetime.datetime) -> bool:
        return cls._is_vm_rezilion_scanner_instance(vm) \
            and cls._not_scanned_since(vm, not_scanned_since) \
            and cls._is_vm_running(vm) \
            and cls._is_supported_host(vm)

    @classmethod
    def _is_vm_rezilion_scanner_instance(cls, vm: azure.mgmt.compute.models.VirtualMachine) -> bool:
        return vm.name != AzureApi().current_vm_name

    @classmethod
    def _not_scanned_since(cls, vm: azure.mgmt.compute.models.VirtualMachine, not_scanned_since: datetime.datetime) -> bool:
        last_scanned = cls._last_scanned(vm)
        if last_scanned is None:
            return True
        return last_scanned < not_scanned_since

    @classmethod
    def _last_scanned(cls, vm: azure.mgmt.compute.models.VirtualMachine) -> datetime.datetime:
        if vm.tags is None:
            return None
        rezilion_scanned = vm.tags.get('rezilion-scanned', None)
        if rezilion_scanned is None:
            return None
        return common_methods.parse_timestamp(rezilion_scanned)

    @classmethod
    def _is_vm_running(cls, vm: azure.mgmt.compute.models.VirtualMachine) -> bool:
        client_vm = AzureClient("virtual_machines")
        expanded_vm = client_vm.get(client_vm.resource_group_name, vm.name, expand="InstanceView")
        instance_view = expanded_vm.instance_view
        return instance_view.statuses[1].display_status.lower() == "vm running"

    @classmethod
    def _is_supported_host(cls, vm: azure.mgmt.compute.models.VirtualMachine) -> bool:
        azure_client = AzureClient('disks')
        os_disk_name = vm.storage_profile.os_disk.name
        os_disk = azure_client.get(azure_client.resource_group_name, os_disk_name)
        vm_architecture = os_disk.supported_capabilities.architecture
        vm_os_type = vm.storage_profile.os_disk.os_type
        return vm_os_type.lower() != "windows" and not vm_architecture.lower().startswith("arm")

