from dataclasses import dataclass


@dataclass
class FileInfo:
    name: str
    end_timestamp: int
    link: str
