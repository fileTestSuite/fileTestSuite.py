from enum import IntEnum
from struct import unpack


class ArgType(IntEnum):
	blob = 0
	int = 1
	string = 2
	double = 3


class ArgParser:
	__slots__ = ()

	def parse(self, binary: bytes):
		raise NotImplementedError


class BlobParser(ArgParser):
	__slots__ = ()

	def parse(self, binary: bytes):
		return binary


class IntParser(ArgParser):
	__slots__ = ()

	def parse(self, binary: bytes):
		return unpack("<I", binary)[0]


class StrParser(ArgParser):
	__slots__ = ()

	def parse(self, binary: bytes):
		return binary.decode("utf-8")


class DoubleParser(ArgParser):
	__slots__ = ()

	def parse(self, binary: bytes):
		return unpack("<d", binary)[0]
