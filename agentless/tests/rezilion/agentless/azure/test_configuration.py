import os
import pytest
from unittest.mock import patch
import rezilion.agentless.azure.configuration
from rezilion.agentless.azure.configuration import AzureConfiguration
from mockito import when, mock


def test_init_configuration__missing_config_environment_variable__exception_raised():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            AzureConfiguration()


def test_get_secret__found_secret_value():
    with patch.dict(os.environ, {'REZILION_SECRET_NAME': 'the-secret-name'}, clear=True):
        secret_client_mock = mock()
        secret_mock = mock({'name': 'key_name'})
        secret_value_mock = mock({'value': 'the-secret'})
        when(rezilion.agentless.azure.configuration).AzureClient('secrets', vault_url="https://the-secret-name.vault.azure.net/").thenReturn(secret_client_mock)
        when(secret_client_mock).list_properties_of_secrets().thenReturn([secret_mock])
        when(secret_client_mock).get_secret('key_name').thenReturn(secret_value_mock)
        config = AzureConfiguration()
        assert config.key_name == 'the-secret'
