import logging
import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    @staticmethod
    def _build_manpage() -> None:
        """Build manpages."""
        manpages = ("dotbackup.1", "dotsetup.1")
        logger = logging.getLogger(__name__)

        for manpage in manpages:
            command = ("asciidoctor", "-b", "manpage", f"{manpage}.adoc")
            logger.info(f"running command: {' '.join(command)}")
            subprocess.check_call(command)

    def initialize(self, version: str, build_data: dict) -> None:
        self._build_manpage()
