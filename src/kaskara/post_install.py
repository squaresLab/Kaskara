# -*- coding: utf-8 -*-
"""
This module is used to install Kaskara's various language backends following
the installation of the Kaskara Python package via setuptools/pip.
"""
__all__ = ('post_install',)

from loguru import logger

from .clang import post_install as post_install_clang


def post_install() -> None:
    logger.info('performing post-installation of Kaskara')
    post_install_clang()
    logger.info('completed post-installation of Kaskara')
