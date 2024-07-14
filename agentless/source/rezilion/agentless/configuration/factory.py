from rezilion.agentless.azure.configuration import AzureConfiguration
from rezilion.agentless import common as common_methods


class ConfigurationFactory:

    @staticmethod
    def get():
        if common_methods.is_in_azure():
            return AzureConfiguration()
