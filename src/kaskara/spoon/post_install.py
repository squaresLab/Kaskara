"""Responsible for installing the backend for the Spoon plugin."""
__all__ = ("post_install",)

import contextlib

import docker
import pkg_resources
from loguru import logger

from kaskara.spoon.common import (
    IMAGE_ID_LABEL,
    IMAGE_NAME,
    PLUGIN_LABEL,
    PLUGIN_LABEL_VALUE,
    VERSION_LABEL,
    VOLUME_LOCATION,
    VOLUME_NAME,
)


def post_install(*, force: bool = False) -> None:
    """Installs the Spoon plugin backend."""
    logger.info("installing Spoon plugin backend")
    backend_directory = pkg_resources.resource_filename(__name__, "backend")
    kaskara_version = pkg_resources.get_distribution("kaskara").version
    logger.debug(f"backend located at: {backend_directory}")

    with contextlib.closing(docker.from_env()) as docker_client:
        logger.trace("prepared Docker client for Spoon backend installation")

        # does the image already exist?
        image: docker.models.images.Image | None = None
        try:
            image = docker_client.images.get(IMAGE_NAME)
        except docker.errors.ImageNotFound:
            logger.info("Spoon plugin Docker image doesn't exist")

        image, _ = docker_client.images.build(
            path=backend_directory,
            tag=IMAGE_NAME,
            labels={
                PLUGIN_LABEL: PLUGIN_LABEL_VALUE,
                VERSION_LABEL: kaskara_version,
            },
        )

        volume: docker.models.volumes.Volume | None = None
        try:
            volume = docker_client.volumes.get(VOLUME_NAME)
            logger.info("found Spoon plugin Docker volume")
        except docker.errors.NotFound:
            logger.info("Spoon plugin Docker volume doesn't exist")
        else:
            volume_labels = volume.attrs.get("Labels", {})
            if volume_labels.get(IMAGE_ID_LABEL) != image.id:
                logger.info("Spoon plugin Docker volume is out-of-date")
                volume.remove()
                volume = None

        if force or volume is None:
            logger.info("creating Spoon plugin Docker volume")

            # create an empty volume
            volume = docker_client.volumes.create(
                name=VOLUME_NAME,
                labels={
                    PLUGIN_LABEL: PLUGIN_LABEL_VALUE,
                    IMAGE_ID_LABEL: image.id,
                },
            )

            # create a container to populate the volume
            assert isinstance(image.id, str)
            docker_client.containers.run(
                image=image.id,
                command="/bin/sh",
                remove=True,
                volumes=[f"{VOLUME_NAME}:{VOLUME_LOCATION}"],
            )

    logger.info("installed Spoon plugin backend")
