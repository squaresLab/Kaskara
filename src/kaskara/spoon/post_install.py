# -*- coding: utf-8 -*-
"""
This module is responsible for installing the backend for the Spoon plugin.
"""
__all__ = ('post_install,')

import contextlib
import pkg_resources

from loguru import logger
import docker

IMAGE_NAME: str = 'christimperley/kaskara:spoon'


def post_install() -> None:
    """Installs the Spoon plugin backend."""
    logger.info('installing Spoon plugin backend')
    backend_directory = pkg_resources.resource_filename(__name__, 'backend')
    logger.debug(f'backend located at: {backend_directory}')
    with contextlib.closing(docker.from_env()) as docker_client:
        logger.debug('prepared Docker client for Spoon backend installation')
        image, _ = docker_client.images.build(path=backend_directory,
                                              tag=IMAGE_NAME,
                                              pull=True)
        logger.info(f"built Docker image for Spoon plugin: {image.tags}")
    logger.info('installed Spoon plugin backend')
