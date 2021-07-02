import typing
from pathlib import Path

from .. import ParsedMetadataJSONLikeT

metaFileName = "meta"

class Serializer:
	@classmethod
	def parse(cls, inp: typing.Any) -> typing.Any:
		raise NotImplementedError

	@classmethod
	def serialize(cls, node, out: typing.Any) -> None:
		raise NotImplementedError

class IFormat(Serializer):
	__slots__ = ()

	@classmethod
	def parse(cls, inp: typing.Any) -> typing.Any:
		return getattr(cls, node.__class__.__name__).parse(node, inp)

	@classmethod
	def serialize(cls, node, out: typing.Any) -> None:
		getattr(cls, node.__class__.__name__).serialize(node, out)

	@property
	def metaFileName(self):
		return metaFileName + "." +self.metaFileExt

	def loadMetadataFile(self):
		raise NotImplementedError

	def parseMetadata(self):
		raise NotImplementedError

	def serializeMetadata(self):
		raise NotImplementedError

	def dumpMetadataFile(self):
		raise NotImplementedError
