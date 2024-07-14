import pytest
from mockito import when, mock
import rezilion.agentless.azure.api
from rezilion.agentless.azure.api import AzureApi, AZURE_RESOURCE_GROUP_NAME_URL, AZURE_SUBSCRIPTION_ID_URL, \
    AZURE_CURRENT_VM_ID_URL, AZURE_CURRENT_VM_NAME_URL, AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS


@pytest.fixture
def mock_http_request(request):
    mock_req_obj = mock()
    mock_http_request = mock()
    when(rezilion.agentless.azure.api).Request(request.param, headers={'Metadata': 'true'}).thenReturn(mock_req_obj)
    when(rezilion.agentless.azure.api).urlopen(mock_req_obj, timeout=AZURE_METADATA_SERVER_TIMEOUT_IN_SECONDS).thenReturn(mock_http_request)
    when(mock_http_request).__enter__().thenReturn(mock_http_request)
    when(mock_http_request).__exit__(None, None, None).thenReturn()
    return mock_http_request


@pytest.mark.parametrize('mock_http_request', [AZURE_RESOURCE_GROUP_NAME_URL], indirect=True)
def test_urlopen__azure_resource_group_name_url__expected_resource_group_name(mock_http_request):
    when(mock_http_request).read().thenReturn(b"resource_group_name")
    result = AzureApi().resource_group_name
    assert result == "resource_group_name"


@pytest.mark.parametrize('mock_http_request', [AZURE_SUBSCRIPTION_ID_URL], indirect=True)
def test_urlopen__azure_subscription_id_url__expected_subscription_id(mock_http_request):
    when(mock_http_request).read().thenReturn(b"subscription_id")
    result = AzureApi().subscription_id
    assert result == "subscription_id"


@pytest.mark.parametrize('mock_http_request', [AZURE_CURRENT_VM_ID_URL], indirect=True)
def test_urlopen__azure_current_vm_id_url__expected_current_vm_id(mock_http_request):
    when(mock_http_request).read().thenReturn(b"current_vm")
    result = AzureApi().current_vm_id
    assert result == "current_vm"


@pytest.mark.parametrize('mock_http_request', [AZURE_CURRENT_VM_NAME_URL], indirect=True)
def test_urlopen__azure_current_vm_name_url__expected_current_vm_name(mock_http_request):
    when(mock_http_request).read().thenReturn(b"current_vm_name")
    result = AzureApi().current_vm_name
    assert result == "current_vm_name"
