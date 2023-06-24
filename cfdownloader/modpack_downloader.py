import os

from .file_reader import ModpackFile
from .mod_downloader import HttpSession


def search_for_modpack() -> str:
    """Utility function to search for a modpack"""
    possible_modpacks = []
    idx = 1

    for file in os.listdir():
        if file.endswith(".zip"):
            possible_modpacks.append(file)
            print(f"{idx}: {file}")
            idx += 1

    if not possible_modpacks:
        print("No modpacks found, enter the path to the modpack zip file.")

        while True:
            file_path = input("File path: ")

            if os.path.isfile(file_path) and file_path.lower().endswith(".zip"):
                return file_path

            print("Please enter a valid path to a zip file.")

    while True:
        try:
            choice = int(input("Which modpack would you like to download? "))
            if 1 <= choice <= len(possible_modpacks):
                return possible_modpacks[choice - 1]
            print(f"Please enter a number between 1 and {len(possible_modpacks)}.")

        except ValueError:
            print("Please enter a number.")


class ModpackDownloader:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty.")
        self.api_key = api_key

    def download_modpack(self, file_path: str = None, output_dir: str = "downloaded_modpacks") -> None:
        """Downloads a modpack from curseforge.

        Args:
            file_path (str): The path to the zip file.
            output_dir (str, optional): The directory to download the mods to. Defaults to "downloaded_modpacks".
        """
        if file_path is None:
            file_path = search_for_modpack()

        modpack = ModpackFile(file_path, output_dir)
        modpack.unzip_and_extract()

        project_ids, file_ids = modpack.get_project_file_ids()
        print(f"Detected {len(project_ids)} mods.")

        with HttpSession(self.api_key) as session:
            mod_data = session.get_mod_data(project_ids, file_ids)
            session.download_mods(mod_data, modpack.output_dir)
            # session.alternate_download_data(modpack.manifest_data, modpack.output_dir)

        input("Press enter to exit.")
