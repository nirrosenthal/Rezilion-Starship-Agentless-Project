from rezilion.agentless.azure.client import AzureClient
import os


class AzureConfiguration:
    def __init__(self):
        try:
            key_vault_name = os.environ['REZILION_SECRET_NAME']
        except KeyError:
            raise ValueError("configurations are missing")

        vault_url = f"https://{key_vault_name}.vault.azure.net/"
        self._secret_client = AzureClient('secrets', vault_url=vault_url)
        self._configuration = self._get_secrets()

    def __getattr__(self, item: str):
        return self._configuration[item]

    def _get_secrets(self) -> dict:
        secrets_dict = {}
        for secret in self._secret_client.list_properties_of_secrets():
            secret_name = secret.name
            secret_value = self._secret_client.get_secret(secret_name).value
            secrets_dict[secret_name] = secret_value
        return secrets_dict
