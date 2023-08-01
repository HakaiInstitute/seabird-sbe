"""
This module contains the Batch class.

The Batch class allows for the chaining of SBE commands to run on data. This
is useful for running multiple commands on the same data without having to
write the data to disk between each command.
"""
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

from seabird_processing.configs import _SBEConfig


class Batch(object):
    """A pipeline of SBE commands to run on data.

    This class allows for the chaining of SBE commands to run on data. This is
    useful for running multiple commands on the same data without having to
    write the data to disk between each command.
    """

    config_header_comment = "@ Generated by the seabird-processing Python package"

    def __init__(self, stages: Iterable[_SBEConfig]):
        """
        Args:
            stages: (Iterable[_SBECommand]) The stages to run on the data
        Returns:
            Pipeline: The pipeline object
        """
        super().__init__()
        self.stages = stages

    def get_batch_config_str(self, input_file_pattern: str) -> str:
        """Get the batch configuration string.

        Args:
            input_file_pattern (str): A pattern to match initial input files
        Returns:
            str: The batch configuration string
        """
        batch_config_str = [self.config_header_comment]
        next_input_file = input_file_pattern
        for config in self.stages:
            batch_config_str.append(
                config.get_exec_str(next_input_file, batch_mode=True)
            )
            next_input_file = Path(config.output_file_path(next_input_file)).name

        return "\n".join(batch_config_str)

    def __call__(self, input_file_pattern: str):
        """Run the pipeline on the data.

        Args:
            input_file_pattern (str): A pattern to match initial input files
        Returns:
            str: The processed data
        """
        with NamedTemporaryFile("w", suffix=".txt") as config_file:
            config_file.write(self.get_batch_config_str(input_file_pattern))
            config_file.flush()
            subprocess.run(
                [
                    "sbebatch",
                    config_file.name,
                ],
                check=True,
            )