# -*- coding: utf-8 -*-
"""
This module is responsible for installing the backend for the C++ plugin.
"""
__all__ = ('post_install,')

import contextlib
import pkg_resources

from loguru import logger
import docker

IMAGE_NAME: str = 'christimperley/kaskara:cpp'


def post_install() -> None:
    """Installs the C++ plugin backend."""
    logger.info('installing C++ plugin backend')
    backend_directory = pkg_resources.resource_filename(__name__, 'backend')
    logger.debug(f'backend located at: {backend_directory}')
    with contextlib.closing(docker.from_env()) as docker_client:
        logger.debug('prepared Docker client for C++ backend installation')
        image, _ = docker_client.images.build(path=backend_directory,
                                              tag=IMAGE_NAME,
                                              pull=True)
        logger.info(f"built Docker image for C++ plugin: {image.tags}")
    logger.info('installed C++ plugin backend')
