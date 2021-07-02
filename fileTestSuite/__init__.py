import typing
from enum import IntEnum


class _SlottedRepr:
	__slots__ = ()

	def __repr__(self):
		return self.__class__.__name__ + "(" + ", ".join(repr(getattr(self, k)) for k in self.__class__.__slots__) + ")"


class Parameter(_SlottedRepr):
	__slots__ = ("id", "value")

	def __init__(self, iD, value):
		self.id = iD
		self.value = value


class FilesSubset(_SlottedRepr):
	__slots__ = ("globMask", "parameters")

	def __init__(self, globMask, parameters):
		self.globMask = globMask
		self.parameters = parameters


PROHIBITED_CHARS_IN_EXT = {"\\", "/"}


class FTSMetadata(_SlottedRepr):
	__slots__ = ("rawExt", "processedExt", "subSets")

	validSignature = "ftsmeta"

	def __init__(self, rawExt: str, processedExt: str, subSets: typing.List[FilesSubset]) -> None:
		self.rawExt = rawExt
		self.processedExt = processedExt
		self.subSets = subSets

		if set(self.rawExt) & PROHIBITED_CHARS_IN_EXT:
			raise ValueError("Raw extension contains prohibited chars", PROHIBITED_CHARS_IN_EXT, self.rawExt)

		if set(self.processedExt) & PROHIBITED_CHARS_IN_EXT:
			raise ValueError("Processed extension contains prohibited chars", PROHIBITED_CHARS_IN_EXT, self.processedExt)


class OnthArg(_SlottedRepr):
	__slots__ = ("id", "type", "name")

	def __init__(self, iD, typ, name):
		self.id = iD
		self.type = typ
		self.name = name


class Onthology(_SlottedRepr):
	__slots__ = ("enum", "types")

	def __init__(self, params):
		enum = IntEnum(name, tuple((el.name, el.id) for el in params))
		self.enum = enum
		self.types = {enum(el.id): el.type for el in params}


ParsedMetadataJSONLikeT = typing.Dict[str, typing.Union[str, "ParsedMetadataJSONLikeT"]]
