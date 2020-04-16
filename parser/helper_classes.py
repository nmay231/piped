from dataclasses import dataclass
import typing


@dataclass
class ReceiveEntry:
    name: str
    arguments: typing.List[int]
    return_: str


@dataclass
class Record:
    repr: typing.Dict[str, typing.Any]
    # type: in the future


@dataclass
class NamedTuple:
    repr: typing.List[typing.Tuple[str, typing.Any]]
    # type: in the future


@dataclass
class Tuple:
    repr: typing.List[typing.Any]
    # type: in the future


@dataclass
class List:
    repr: typing.List[typing.Any]
    # type: in the future


@dataclass
class Variable:
    name: str
    value: typing.Any
    type: typing.Any
