__all__ = (
    "IMAGE_NAME",
    "VOLUME_NAME",
    "VOLUME_LOCATION",
    "IMAGE_ID_LABEL",
    "PLUGIN_LABEL",
    "VERSION_LABEL",
)

IMAGE_NAME: str = "christimperley/kaskara:cpp"
VOLUME_NAME: str = "kaskara-clang"
VOLUME_LOCATION: str = "/opt/kaskara"
IMAGE_ID_LABEL: str = "kaskara.built-from-image-id"
PLUGIN_LABEL: str = "kaskara.plugin"
VERSION_LABEL: str = "kaskara.version"
