"""Responsible for installing the backend for the C++ plugin."""
from __future__ import annotations

__all__ = ("post_install",)

import contextlib

import docker
import docker.errors
import pkg_resources
from loguru import logger

IMAGE_NAME: str = "christimperley/kaskara:cpp"
VOLUME_NAME: str = "kaskara-clang"
VOLUME_LOCATION: str = "/opt/kaskara"
IMAGE_ID_LABEL: str = "kaskara.built-from-image-id"
PLUGIN_LABEL: str = "kaskara.plugin"
VERSION_LABEL: str = "kaskara.version"

DEFAULT_KASKARA_DIRECTORY: str = "~/.kaskara"


def post_install(
    kaskara_directory: str = DEFAULT_KASKARA_DIRECTORY,
    *,
    force: bool = False,
) -> None:
    """Installs the C++ plugin backend."""
    logger.info("installing C++ plugin backend")
    backend_directory = pkg_resources.resource_filename(__name__, "backend")
    kaskara_version = pkg_resources.get_distribution("kaskara").version
    logger.trace(f"backend located at: {backend_directory}")

    with contextlib.closing(docker.from_env()) as docker_client:
        logger.trace("prepared Docker client for C++ backend installation")

        # does the image already exist?
        image: docker.models.images.Image | None = None
        try:
            image = docker_client.images.get(IMAGE_NAME)
        except docker.errors.ImageNotFound:
            logger.info("C++ plugin Docker image doesn't exist")

        image, _ = docker_client.images.build(
            path=backend_directory,
            tag=IMAGE_NAME,
            pull=True,
            labels={
                PLUGIN_LABEL: "clang",
                VERSION_LABEL: kaskara_version,
            },
        )

        volume: docker.models.volumes.Volume | None = None
        try:
            volume = docker_client.volumes.get(VOLUME_NAME)
        except docker.errors.NotFound:
            logger.info("C++ plugin Docker volume doesn't exist")
        else:
            volume_labels = volume.attrs.get("Labels", {})
            if volume_labels.get(IMAGE_ID_LABEL) != image.id:
                logger.info("C++ plugin Docker volume is out-of-date")
                volume.remove()
                volume = None

        if force or volume is None:
            logger.info("creating C++ plugin Docker volume")

            # create an empty volume
            volume = docker_client.volumes.create(
                name=VOLUME_NAME,
                labels={
                    PLUGIN_LABEL: "clang",
                    IMAGE_ID_LABEL: image.id,
                },
            )

            # create a container to populate the volume
            assert isinstance(image.id, str)
            docker_client.containers.run(
                image=image.id,
                command="true",
                remove=True,
                volumes=[f"{VOLUME_NAME}:{VOLUME_LOCATION}"],
            )

    logger.info("installed C++ plugin backend")
