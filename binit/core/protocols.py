from typing import IO, Protocol


class YamlProtocol(Protocol):
    def load(self, stream: IO[str]) -> dict: ...


    def dump(self, data: dict, stream: IO[str]) -> None: ...
