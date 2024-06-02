"""Installs Kaskara's language backends following the installation of this Python package."""
__all__ = ("post_install",)

from loguru import logger

from .clang.post_install import post_install as post_install_clang


def post_install() -> None:
    logger.info("performing post-installation of Kaskara")
    post_install_clang()
    logger.info("completed post-installation of Kaskara")


if __name__ == "__main__":
    post_install()
