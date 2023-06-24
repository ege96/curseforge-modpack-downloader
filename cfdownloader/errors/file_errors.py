class MissingManifestError(Exception):
    """Raised when the manifest file is missing or invalid."""
    pass


class FileTypeMismatchError(Exception):
    """Raised when the file type does not match the expected type."""
    pass


class FileAccessError(Exception):
    """Raised when there is an error accessing a file."""
    pass


class FileDownloadError(Exception):
    """Raised when there is an error downloading a file."""
    pass
