from asyncio import get_event_loop, gather
from os import path, makedirs
from typing import Optional, List

from aiohttp import ClientSession, ClientResponse


class HttpSession:
    """Class for handling HTTP requests."""

    def __init__(self, api_key: str):
        """Initializes the HttpSession class.

        Args:
            api_key (str): The curseforge API key.

        """
        self.api_key: str = api_key
        self.loop = get_event_loop()

        self.session: Optional[ClientSession] = None

    def __enter__(self):
        self.loop.run_until_complete(self._setup_session())
        return self

    async def _setup_session(self) -> None:
        """Sets up the aiohttp session."""
        self.session = ClientSession(headers={"x-api-key": self.api_key})

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.run_until_complete(self._close())

    async def _close(self) -> None:
        """Closes the session."""
        await self.session.close()

    def get_mod_data(self, projectIDs: List[str | int], fileIDs: List[str | int]) -> List[dict]:
        """Gets the data for a list of mods.

        Args:
            projectIDs (List[str|int]): The project ids of the mods.
            fileIDs (List[str|int]): The file ids of the mods.

        Returns:
            List[dict]: The data for the mods.

        """
        return self.loop.run_until_complete(self._get_mod_data(projectIDs, fileIDs))

    async def _get_mod_data(self, projectIDs: List[str | int], fileIDs: List[str | int]) -> List[dict]:
        tasks = []

        for projectID, fileID in zip(projectIDs, fileIDs):
            url = f"https://api.curseforge.com/v1/mods/{projectID}/files/{fileID}"
            tasks.append(self.session.get(url))

        responses: List[ClientResponse] = await gather(*tasks)
        return [await response.json() for response in responses]

    def download_mods(self, mod_data: List[dict], output_dir: str, batch_size: int = 10) -> None:
        """Downloads a list of mods.

        Args:
            mod_data (List[dict]): The data for the mods.
            output_dir (str): The directory to download the mods to.
            batch_size (int): The number of downloads to process in each batch.

        """
        self.loop.run_until_complete(self._download_mods(mod_data, output_dir, batch_size))

    async def _download_mods(self, mod_data: List[dict], output_dir: str, batch_size: int) -> None:
        for i in range(0, len(mod_data), batch_size):
            batch = mod_data[i:i + batch_size]
            await self._process_batch(batch, output_dir)

    async def _process_batch(self, batch: List[dict], output_dir: str) -> None:
        tasks = []

        for mod in batch:
            mod_data = mod["data"]

            if mod_data["isAvailable"] is False:
                print(
                    f"Mod \"{mod_data['fileName']}\" is unavailable on curseforge and may be outdated. Recommend downloading manually.")

            url = mod_data["downloadUrl"]

            if url is None:
                file_id = str(mod_data["id"])
                name = mod_data["fileName"]
                url = f"https://edge.forgecdn.net/files/{file_id[:4]}/{file_id[4:]}/{name}"

            tasks.append(self.session.get(url))

        responses: List[ClientResponse] = await gather(*tasks)

        for response in responses:
            file_name: str = path.basename(response.url.path)

            if file_name.endswith(".jar"):
                folder = "mods"
            elif file_name.endswith(".zip"):
                folder = "resourcepacks"
            else:
                folder = "misc"

            if not path.exists(path.join(output_dir, folder)):
                makedirs(path.join(output_dir, folder))

            file_path: str = path.join(path.join(output_dir, folder), file_name)

            with open(file_path, "wb") as f:
                f.write(await response.read())

    def alternate_download_data(self, manifest_data: dict, output_dir: str) -> None:
        """Downloads a list of mods.

        Args:
            manifest_data (dict): The data for the mods.
            output_dir (str): The directory to download the mods to.

        """
        self.loop.run_until_complete(self._alternate_download_data(manifest_data, output_dir))

    async def _alternate_download_data(self, manifest_data: dict, output_dir: str) -> None:
        for mod in manifest_data["files"]:
            project_id = mod["projectID"]
            file_id = mod["fileID"]

            url = f"https://www.curseforge.com/api/v1/mods/{project_id}/files/{file_id}/download"

            async with self.session.get(url) as response:
                resp_code = response.status
                print(resp_code)

                if resp_code != 200:
                    print(url)
                    continue

                file_name: str = path.basename(response.url.path)

                if file_name.endswith(".jar"):
                    folder = "mods"
                elif file_name.endswith(".zip"):
                    folder = "resourcepacks"
                else:
                    folder = "misc"

                folder += "_alternate"

                if not path.exists(path.join(output_dir, folder)):
                    makedirs(path.join(output_dir, folder))

                file_path: str = path.join(path.join(output_dir, folder), file_name)

                with open(file_path, "wb") as f:
                    f.write(await response.read())
