from dataclasses import dataclass


@dataclass
class FileInfo:
    name: str
    till: int
    link: str
