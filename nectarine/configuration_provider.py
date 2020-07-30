from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Tuple, Type

Path = Tuple[str, ...]


class ConfigurationProvider(metaclass=ABCMeta):
    """
    Abstract base class for configuration providers
    """

    @abstractmethod
    def load_configuration(self, target_type: Type, strict=False) -> Dict[str, Any]:
        """
        Load the configuration for a given type

        :param target_type:             the type to load the configuration for
        :param strict:                  whether or not strict mode should be used (see each provider's documentation)
        """
        pass
