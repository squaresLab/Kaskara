__all__ = (
    "IMAGE_ID_LABEL",
    "IMAGE_NAME",
    "JAVA_PATH",
    "PLUGIN_LABEL",
    "PLUGIN_LABEL_VALUE",
    "VERSION_LABEL",
    "VOLUME_LOCATION",
    "VOLUME_NAME",
)

IMAGE_ID_LABEL: str = "kaskara.built-from-image-id"
IMAGE_NAME: str = "christimperley/kaskara:spoon"
JAR_PATH: str = "/opt/kaskara-spoon/kaskara-spoon.jar"
JAVA_PATH: str = "java"
PLUGIN_LABEL: str = "kaskara.plugin"
PLUGIN_LABEL_VALUE: str = "spoon"
VERSION_LABEL: str = "kaskara.version"
VOLUME_LOCATION: str = "/opt/kaskara-spoon"
VOLUME_NAME: str = "kaskara-spoon"
