from dataclasses import dataclass
import typing


class HoldPlease:
    pass  # simple class as a dynamic data store


@dataclass
class ReceiveEntry:
    name: str
    arguments: typing.List[int]
    return_: str
    body: typing.Any

    def generate(self):
        return (
            f"void receive_entry_{self.name}(void)"
            "{\n  " + "\n  ".join(stm.generate() for stm in self.body) + "\n}"
        )


@dataclass
class Record:
    repr: typing.Dict[str, typing.Any]
    # type: in the future

    def generate(self):
        # This needs to be based off of its type in the future so that
        # the items are not out of order or something like that
        return "{" f'{", ".join(val.generate() for val in self.repr.values())}' "}"


@dataclass
class NamedTuple:
    repr: typing.List[typing.Tuple[str, typing.Any]]
    # type: in the future

    def generate(self):
        # This needs to be based off of its type in the future so that
        # the items are not out of order or something like that
        return "{" f'{", ".join(x[1].generate() for x in self.repr)}' "}"


@dataclass
class Tuple:
    repr: typing.List[typing.Any]
    # type: in the future


@dataclass
class List:
    repr: typing.List[typing.Any]
    # type: in the future


@dataclass
class Integer:
    repr: str

    def generate(self):
        return self.repr


@dataclass
class Float:
    repr: str

    def generate(self):
        return self.repr


@dataclass
class String:
    repr: str

    def generate(self):
        # Force double quotes
        return f'"{eval(self.repr)}"'


@dataclass
class Variable:
    name: str
    value: typing.Any
    type: typing.Any
