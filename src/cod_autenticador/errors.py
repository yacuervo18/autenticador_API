class CodAutenticadorError(Exception):
    """Error base del componente."""


class ConfigurationError(CodAutenticadorError):
    """La configuración no es válida."""


class StorageNotFoundError(CodAutenticadorError):
    """No se encontró el almacenamiento solicitado."""


class UnsupportedStorageError(CodAutenticadorError):
    """El almacenamiento no tiene un formato reconocido."""
