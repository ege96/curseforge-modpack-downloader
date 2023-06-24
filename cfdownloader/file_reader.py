from json import load, JSONDecodeError
from os import path, makedirs
from shutil import copytree, rmtree
from tempfile import TemporaryDirectory
from typing import Optional
from zipfile import ZipFile

from .errors import FileTypeMismatchError, MissingManifestError


class ModpackFile:
    """Class for reading all data related to a curseforge zip file."""

    def __init__(self, file_path: str, output_dir: str = "downloaded_modpacks"):
        """Initializes the ModpackFile class.

        Args:
            file_path (str): The path to the zip file.

        """
        self.file_path: str = file_path
        self.file_name: str = path.splitext(path.basename(self.file_path))[0]

        self.output_dir: str = path.join(output_dir, self.file_name)

        self.manifest_data: Optional[dict] = None

        self._check_file_path()
        self._setup_output_dir()

    def _check_file_path(self) -> None:
        """Checks if the file path is valid.

        Raises:
            FileNotFoundError: If the file path is invalid.
            FileTypeMismatchError: If the file is not a zip file.

        """
        if not path.isfile(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} does not exist.")

        else:
            # check if the file is a zip file
            if not self.file_path.endswith(".zip"):
                raise FileTypeMismatchError(f"File {self.file_path} is not a zip file.")

    def _setup_output_dir(self) -> None:
        """Creates the output directory if it does not exist."""
        if not path.isdir(self.output_dir):
            makedirs(self.output_dir)

        else:
            # remove all files in the output directory
            rmtree(self.output_dir, ignore_errors=True)
            makedirs(self.output_dir)

    def unzip_and_extract(self) -> None:
        """Unzips the file to the destination.

        Raises:
            MissingManifestError: If the manifest file is missing or invalid.

        """
        with TemporaryDirectory() as temp_dir:

            with ZipFile(self.file_path, "r") as zip_file:
                zip_file.extractall(temp_dir)

            # read manifest.json
            try:
                with open(path.join(temp_dir, "manifest.json"), "r") as manifest_file:
                    self.manifest_data = load(manifest_file)

            except (FileNotFoundError, JSONDecodeError):
                raise MissingManifestError("Manifest file is missing.")

            # copy overrides folder to output_dir
            copytree(path.join(temp_dir, "overrides"), self.output_dir, dirs_exist_ok=True)

    def get_project_file_ids(self) -> tuple[list[str | int], list[str | int]]:
        """Gets the project ids and file ids of the mods in the modpack.

        Returns:
            tuple[list[str|int], list[str|int]]: The project ids and file ids of the mods in the modpack.

        """
        project_ids = []
        file_ids = []

        for mod in self.manifest_data["files"]:
            project_ids.append(mod["projectID"])
            file_ids.append(mod["fileID"])

        return project_ids, file_ids
