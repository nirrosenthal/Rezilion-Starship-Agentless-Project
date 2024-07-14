from datetime import datetime
import pytest
import rezilion.agentless.azure.compute
from rezilion.agentless.azure.compute import VirtualMachine
from rezilion.agentless import common, constants
from mockito import when, mock
from unittest.mock import patch
from rezilion.agentless.azure.disk import Disk


FAKE_TIMESTAMP = '2023-05-08 15:53:55'
NOT_SCANNED_SINCE = datetime.strptime(FAKE_TIMESTAMP, constants.DATETIME_FORMAT)
OLDER_SCAN = "2023-04-30 19:25:35"
NEWER_SCAN = "2023-05-09 00:01:02"


@pytest.fixture
def client_vm_mock():
    mock_client = mock({'resource_group_name': 'resource_group', 'current_vm_name': 'rezilion_scanner_vm'})
    return mock_client


@pytest.fixture
def vm_scan_time_mock(request):
    return request.param


@pytest.fixture
def vm_os_type_mock(request):
    return request.param


@pytest.fixture
def vm_properties_mock(request, client_vm_mock, vm_scan_time_mock, vm_os_type_mock):
    os_disk_mock = mock({'os_type': vm_os_type_mock, 'name': "disk_name"})
    storage_profile_mock = mock({'os_disk': os_disk_mock})
    vm_mock = mock({'name': request.param, 'tags': {'rezilion-scanned': vm_scan_time_mock}, 'storage_profile': storage_profile_mock})
    when(rezilion.agentless.azure.compute).AzureClient("virtual_machines").thenReturn(client_vm_mock)
    when(rezilion.agentless.azure.compute).AzureApi().thenReturn(client_vm_mock)
    when(client_vm_mock).list(client_vm_mock.resource_group_name).thenReturn([vm_mock])
    return vm_mock


@pytest.fixture
def vm_running_state_mock(request, client_vm_mock, vm_properties_mock):
    display_status_mock = mock({'display_status': request.param})
    instance_view_mock = mock({'statuses': [None, display_status_mock]})
    expanded_vm_mock = mock({'instance_view': instance_view_mock})
    when(client_vm_mock).get(client_vm_mock.resource_group_name, vm_properties_mock.name, expand="InstanceView").thenReturn(expanded_vm_mock)
    return instance_view_mock


@pytest.fixture
def vm_architecture_mock(request, vm_properties_mock):
    client_disk_mock = mock({'resource_group_name': 'resource_group', 'current_vm_name': 'rezilion_scanner_vm'})
    supported_capabilities_mock = mock({'architecture': request.param})
    os_disk_mock = mock({'supported_capabilities': supported_capabilities_mock})
    disk_name = vm_properties_mock.storage_profile.os_disk.name
    when(rezilion.agentless.azure.compute).AzureClient("disks").thenReturn(client_disk_mock)
    when(client_disk_mock).get(client_disk_mock.resource_group_name, disk_name).thenReturn(os_disk_mock)
    return os_disk_mock


@pytest.fixture
def vm_mock(request):
    azure_api_mock = mock({'resource_group_name': 'resource_group'})
    azure_client_mock = mock({'subscription_id': 'fake-subscription-id'})
    vm_mock = mock({'tags': request.param})
    when(rezilion.agentless.azure.compute).AzureApi().thenReturn(azure_api_mock)
    when(rezilion.agentless.azure.compute).AzureClient("virtual_machines").thenReturn(azure_client_mock)
    when(azure_client_mock).get(resource_group_name='resource_group', vm_name='vm_name').thenReturn(vm_mock)
    return vm_mock


@pytest.fixture
def storage_devices_mock(client_vm_mock):
    os_disk_mock = mock({'name': "os_disk_name"})
    storage_profile_mock = mock({'os_disk': os_disk_mock, 'data_disks': [mock({'name': "data_disk_name"})]})
    vm_mock = mock({'name': "vm_name", "storage_profile": storage_profile_mock})
    when(rezilion.agentless.azure.compute).AzureApi().thenReturn(client_vm_mock)
    when(rezilion.agentless.azure.compute).AzureClient("virtual_machines").thenReturn(client_vm_mock)
    when(client_vm_mock).get(resource_group_name=client_vm_mock.resource_group_name, vm_name="vm_name").thenReturn(vm_mock)

class MockDisk:
    def __init__(self, disk_id, scanned_compute_id, is_root_device):
        self.id = disk_id
        self.is_root_device = is_root_device

    @staticmethod
    def supported(disk_id: str):
        return Disk.supported(disk_id)


@pytest.mark.parametrize('vm_mock', [None], indirect=True)
def test_tag_scanned__no_tags_at_all__successfully_tag_vm(vm_mock):
    expected_output = {'rezilion-scanned': FAKE_TIMESTAMP}
    when(common).generate_timestamp().thenReturn(FAKE_TIMESTAMP)
    tested = VirtualMachine(vm_name='vm_name')
    tested.tag_scanned()
    assert vm_mock.tags == expected_output


@pytest.mark.parametrize('vm_mock', [{'some-tag': FAKE_TIMESTAMP}], indirect=True)
def test_tag_scanned__tags_dict_exists__successfully_tag_vm(vm_mock):
    expected_output = {'some-tag': FAKE_TIMESTAMP, 'rezilion-scanned': FAKE_TIMESTAMP}
    when(common).generate_timestamp().thenReturn(FAKE_TIMESTAMP)
    tested = VirtualMachine(vm_name='vm_name')
    tested.tag_scanned()
    assert vm_mock.tags == expected_output


@pytest.mark.parametrize('vm_properties_mock', ["vm_name"], indirect=True)
@pytest.mark.parametrize('vm_scan_time_mock', [OLDER_SCAN], indirect=True)
@pytest.mark.parametrize('vm_running_state_mock', ["VM running"], indirect=True)
@pytest.mark.parametrize('vm_architecture_mock', ["x64"], indirect=True)
@pytest.mark.parametrize('vm_os_type_mock', ["Linux"], indirect=True)
def test_find__sanity__expected_mock_compute(vm_properties_mock, vm_running_state_mock,
                                             vm_architecture_mock):
    mock_compute_vm = mock()
    when(rezilion.agentless.azure.compute).VirtualMachine(vm_properties_mock.name).thenReturn(mock_compute_vm)
    vms = [vm for vm in VirtualMachine.find(NOT_SCANNED_SINCE)]
    assert len(vms) == 1 and vms[0] == mock_compute_vm


@pytest.mark.parametrize('vm_properties_mock', ["vm_name"], indirect=True)
@pytest.mark.parametrize('vm_scan_time_mock', [OLDER_SCAN], indirect=True)
@pytest.mark.parametrize('vm_running_state_mock', ["VM running"], indirect=True)
@pytest.mark.parametrize('vm_architecture_mock', ["Arm64"], indirect=True)
@pytest.mark.parametrize('vm_os_type_mock', ["Linux"], indirect=True)
def test_find__not_supported_arm__expected_empty_list(vm_properties_mock, vm_running_state_mock, vm_architecture_mock):
    vms = [vm for vm in VirtualMachine.find(NOT_SCANNED_SINCE)]
    assert len(vms) == 0


@pytest.mark.parametrize('vm_properties_mock', ["vm_name"], indirect=True)
@pytest.mark.parametrize('vm_scan_time_mock', [OLDER_SCAN], indirect=True)
@pytest.mark.parametrize('vm_running_state_mock', ["VM running"], indirect=True)
@pytest.mark.parametrize('vm_architecture_mock', ["x64"], indirect=True)
@pytest.mark.parametrize('vm_os_type_mock', ["Windows"], indirect=True)
def test_find__not_supported_windows__expected_empty_list(vm_properties_mock, vm_running_state_mock, vm_architecture_mock):
    vms = [vm for vm in VirtualMachine.find(NOT_SCANNED_SINCE)]
    assert len(vms) == 0


@pytest.mark.parametrize('vm_properties_mock', ["vm_name"], indirect=True)
@pytest.mark.parametrize('vm_scan_time_mock', [OLDER_SCAN], indirect=True)
@pytest.mark.parametrize('vm_running_state_mock', ["VM deallocated"], indirect=True)
@pytest.mark.parametrize('vm_os_type_mock', ["Linux"], indirect=True)
def test_find__vm_not_running__expected_empty_list(vm_properties_mock, vm_running_state_mock):
    vms = [vm for vm in VirtualMachine.find(NOT_SCANNED_SINCE)]
    assert len(vms) == 0


@pytest.mark.parametrize('vm_properties_mock', ["vm_name"], indirect=True)
@pytest.mark.parametrize('vm_scan_time_mock', [NEWER_SCAN], indirect=True)
@pytest.mark.parametrize('vm_os_type_mock', ["Linux"], indirect=True)
def test_find__vm_already_scanned__expected_empty_list(vm_properties_mock):
    vms = [vm for vm in VirtualMachine.find(NOT_SCANNED_SINCE)]
    assert len(vms) == 0


@pytest.mark.parametrize('vm_properties_mock', ["rezilion_scanner_vm"], indirect=True)
@pytest.mark.parametrize('vm_scan_time_mock', [OLDER_SCAN], indirect=True)
@pytest.mark.parametrize('vm_os_type_mock', ["Linux"], indirect=True)
def test_find__is_rezlilion_scanner_vm__expected_empty_list(vm_properties_mock):
    vms = [vm for vm in VirtualMachine.find(NOT_SCANNED_SINCE)]
    assert len(vms) == 0


@patch('rezilion.agentless.azure.compute.Disk', MockDisk)
def test_storage_devices__sanity__expected_one_disk__expected_first_is_root_device(storage_devices_mock):
    when(MockDisk).supported("os_disk_name").thenReturn(True)
    when(MockDisk).supported("data_disk_name").thenReturn(False)
    tested = VirtualMachine("vm_name")
    disks = [d for d in tested.storage_devices()]
    assert len(disks) == 1 and disks[0].is_root_device and disks[0].id != "data_disk_name"



