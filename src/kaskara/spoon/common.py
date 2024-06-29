__all__ = (
    "BINARY_PATH",
    "IMAGE_ID_LABEL",
    "IMAGE_NAME",
    "PLUGIN_LABEL",
    "PLUGIN_LABEL_VALUE",
    "VERSION_LABEL",
    "VOLUME_LOCATION",
    "VOLUME_NAME",
)

BINARY_PATH: str = "/opt/kaskara-spoon/bin/kaskara-spoon"
IMAGE_ID_LABEL: str = "kaskara.built-from-image-id"
IMAGE_NAME: str = "christimperley/kaskara:spoon"
PLUGIN_LABEL: str = "kaskara.plugin"
PLUGIN_LABEL_VALUE: str = "spoon"
VERSION_LABEL: str = "kaskara.version"
VOLUME_LOCATION: str = "/opt/kaskara-spoon"
VOLUME_NAME: str = "kaskara-spoon"
