import pytest
import rezilion.agentless.configuration.factory
from rezilion.agentless.configuration.factory import ConfigurationFactory
from mockito import when, mock


def test_get__is_in_azure():
    azure_configuration_mock = mock()
    when(rezilion.agentless.configuration.factory.common_methods).is_in_azure().thenReturn(True)
    when(rezilion.agentless.configuration.factory).AzureConfiguration().thenReturn(azure_configuration_mock)
    azure_configuration = ConfigurationFactory().get()
    assert azure_configuration == azure_configuration_mock




