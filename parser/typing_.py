from typing import List, Dict, Any, Union


class Type:
    pass


class TypeMaster:

    registered: Dict[str, Type] = []

    @staticmethod
    def parseType(type_name: str):
        self = TypeMaster

    @staticmethod
    def registerType(type_: Type):
        self = TypeMaster
        self.registered[type_._repr] = Type
