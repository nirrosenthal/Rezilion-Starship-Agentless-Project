from mockito import mock, when
from rezilion.agentless.azure.disk import Disk
from rezilion.agentless.azure.exceptions import AzureOperationError
import rezilion.agentless.azure.disk
import rezilion.agentless.azure.compute
import pytest
import subprocess


@pytest.fixture
def azure_api_mock():
    azure_api_mock = mock({'resource_group_name': "resource_group_name", 'current_vm_name': 'rezilion_vm'})
    when(rezilion.agentless.azure.disk).AzureApi().thenReturn(azure_api_mock)
    return azure_api_mock


@pytest.fixture
def vm_client_mock():
    client_mock = mock()
    when(rezilion.agentless.azure.disk).AzureClient('virtual_machines').thenReturn(client_mock)
    return client_mock


@pytest.fixture
def snapshots_client_mock():
    client_mock = mock()
    when(rezilion.agentless.azure.disk).AzureClient('snapshots').thenReturn(client_mock)
    return client_mock


@pytest.fixture
def disks_client_mock():
    client_mock = mock()
    when(rezilion.agentless.azure.disk).AzureClient('disks').thenReturn(client_mock)
    return client_mock


@pytest.fixture
def rezilion_disk_mock(azure_api_mock, disks_client_mock, vm_client_mock, azure_disk_mock):
    azure_vm_mock = mock()
    when(disks_client_mock).get(resource_group_name="resource_group_name", disk_name="disk_name").thenReturn(azure_disk_mock)
    when(vm_client_mock).get(resource_group_name="resource_group_name", vm_name="vm_name").thenReturn(azure_vm_mock)
    return Disk(disk_id="disk_name", scanned_compute_id="vm_name")


@pytest.fixture
def azure_disk_mock():
    return mock({'name': "disk_name", 'location': 'uksouth', 'id': "disk_id", 'tags': {}})


@pytest.fixture
def mounted_disk_mock(rezilion_disk_mock):
    rezilion_disk_mock._snapshot = mock({'id': "snapshot_id", 'name': "snapshot-disk_name"})
    rezilion_disk_mock._disk_copy = mock({'id': "disk_copy_id", 'name': "disk-snapshot-disk_name"})
    rezilion_disk_mock._device_mount_path_on_host = "dev/sdc1"
    return rezilion_disk_mock


@pytest.fixture
def curr_vm_mock():
    return mock({'name': "rezilion_vm", 'zones': [1], 'storage_profile': mock({'data_disks': [mock({'managed_disk': mock({'id': "disk_id"})})]})})


@pytest.fixture
def curr_vm_mounted_mock(azure_api_mock, vm_client_mock, curr_vm_mock):
    data_disk_mock = mock({"managed_disk": mock({'id': "disk_copy_id"})})
    curr_vm_mock.storage_profile.data_disks.append(data_disk_mock)
    when(vm_client_mock).get(azure_api_mock.resource_group_name, azure_api_mock.current_vm_name).thenReturn(curr_vm_mock)
    return curr_vm_mock


def test_teardown__unmount_fail__expected_error(mounted_disk_mock):
    when(subprocess).run(["sudo", "umount", mounted_disk_mock._device_mount_path_on_host], check=True).thenRaise(Exception)
    with pytest.raises(Exception):
        mounted_disk_mock.teardown()


def test_teardown__delete_snapshot_fail__expected_error(snapshots_client_mock, mounted_disk_mock):
    when(subprocess).run(["sudo", "umount", mounted_disk_mock._device_mount_path_on_host], check=True).thenReturn()
    when(snapshots_client_mock).delete_resource("snapshot-disk_name").thenRaise(AzureOperationError)
    with pytest.raises(AzureOperationError):
        mounted_disk_mock.teardown()


def test_teardown__detach_disk_fail__expected_error(vm_client_mock, snapshots_client_mock, mounted_disk_mock, curr_vm_mounted_mock):
    when(subprocess).run(["sudo", "umount", mounted_disk_mock._device_mount_path_on_host], check=True).thenReturn()
    when(snapshots_client_mock).delete_resource("snapshot-disk_name").thenReturn()
    when(vm_client_mock).update_resource(curr_vm_mounted_mock.name, curr_vm_mounted_mock).thenRaise(AzureOperationError)
    with pytest.raises(AzureOperationError):
        mounted_disk_mock.teardown()


def test_teardown__delete_disk_fail__expected_error(vm_client_mock, snapshots_client_mock, disks_client_mock, mounted_disk_mock, curr_vm_mounted_mock):
    when(subprocess).run(["sudo", "umount", mounted_disk_mock._device_mount_path_on_host], check=True).thenReturn()
    when(snapshots_client_mock).delete_resource("snapshot-disk_name").thenReturn()
    when(vm_client_mock).update_resource(curr_vm_mounted_mock.name, curr_vm_mounted_mock).thenReturn()
    when(disks_client_mock).delete_resource('disk-snapshot-disk_name').thenRaise(AzureOperationError)
    with pytest.raises(AzureOperationError):
        mounted_disk_mock.teardown()


def test_teardown__sanity__expected_teardown(vm_client_mock, snapshots_client_mock, disks_client_mock, mounted_disk_mock, curr_vm_mounted_mock):
    deleted_disk_id = 'disk_copy_id'
    when(subprocess).run(["sudo", "umount", mounted_disk_mock._device_mount_path_on_host], check=True).thenReturn()
    when(snapshots_client_mock).delete_resource("snapshot-disk_name").thenReturn()
    when(vm_client_mock).update_resource(curr_vm_mounted_mock.name, curr_vm_mounted_mock).thenReturn()
    when(disks_client_mock).delete_resource('disk-snapshot-disk_name').thenReturn()
    assert deleted_disk_id in [d.managed_disk.id for d in curr_vm_mounted_mock.storage_profile.data_disks]
    mounted_disk_mock.teardown()
    assert deleted_disk_id not in [d.managed_disk.id for d in curr_vm_mounted_mock.storage_profile.data_disks]

