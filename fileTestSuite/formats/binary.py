import typing
from enum import IntEnum
from io import BytesIO
from pathlib import Path
from struct import pack

from .core import Serializer
from .. import ParsedMetadataJSONLikeT, FTSMetadata, Parameter, FilesSubset, OnthArg, Onthology
from .core import IFormat

formatVersion = (0, 0)


class Version:
	__slots__ = ("major", "minor")

	def __init__(self, major: int, minor: int) -> None:
		self.minor = minor
		self.major = major

class Header:
	__slots__ = ("signature", "version")

	def __init__(self, signature: str, version: Version) -> None:
		self.signature = signature
		self.version = version

class Headered(Serializer):
	__slots__ = ()
	validSignature = None

	@classmethod
	def parse(cls, stream: BytesIO) -> None:
		header = HeaderS.parse(stream)

		if header.signature != cls.validSignature:
			raise ValueError("Wrong signature, " + cls.validSignature + " expected", header.signature)

	@classmethod
	def serialize(cls, self, stream: BytesIO) -> None:
		HeaderS.serialize(Header(self.__class__.validSignature, Version(*formatVersion)), stream)


class VersionS(Serializer):

	@classmethod
	def parse(cls, stream: BytesIO) -> "Version":
		d = stream.read(2)
		return Version(*reversed(d))

	@classmethod
	def serialize(cls, self, stream: BytesIO) -> None:
		stream.write(bytes((self.minor, self.major)))


class HeaderS(Serializer):

	@classmethod
	def parse(cls, stream: BytesIO) -> "Header":
		sigRaw = stream.read(8)
		if sigRaw[-1] == 0:
			sigRaw = sigRaw[:-1]
		else:
			raise ValueError("Signature is not null terminated!")
		return Header(sigRaw.decode(u"utf8"), VersionS.parse(stream))

	@classmethod
	def serialize(cls, self, stream: BytesIO) -> None:
		stream.write(self.signature.encode("utf-8"))
		stream.write(b"\0")
		VersionS.serialize(self.version, stream)


class StrS(Serializer):

	@classmethod
	def parse(cls, stream: BytesIO) -> "Str":
		size = stream.read(1)[0]
		if size != 0:
			raw = stream.read(size + 1)
			if raw[-1] == 0:
				raw = raw[:-1]
			else:
				raise ValueError("Str is not null terminated!")

			return raw.decode(u"utf8")
		return ""

	@classmethod
	def serialize(cls, self, stream: BytesIO) -> None:
		stream.write(bytes((len(self),)))
		stream.write(self.encode("utf-8"))
		stream.write(b"\0")


class ParameterS(Serializer):

	@classmethod
	def parse(cls, stream, onthology):
		iD = stream.read(1)[0]
		size = stream.read(1)[0]
		value = onthology[iD].parse(stream.read(size))
		return Parameter(iD, value)

	@classmethod
	def serialize(cls, obj, stream, onthology):
		binValue = onthology[obj.id].serialize(obj.value)
		stream.write(bytes((obj.id, len(binValue))))
		stream.write(binValue)


class FilesSubsetS(Serializer):

	@classmethod
	def parse(cls, stream, onthology):
		glob_mask = StrS.parse(stream)
		params_count = stream.read(1)[0]
		parameters = [None] * (params_count)
		for i in range(params_count):
			parameters[i] = ParameterS.parse(stream, onthology)

		return FilesSubset(glob_mask, parameters)

	@classmethod
	def serialize(cls, self, stream):
		serialize(self.glob_mask, stream)
		stream.write(bytes((len(self.parameters),)))
		for k, v in self.parameters.items():
			onthology[k].serialize(v, stream)

class FTSMetadataS(Headered):
	validSignature = "ftsmeta"

	@classmethod
	def parse(cls, stream: BytesIO) -> "FTSMetadata":
		super(cls, cls).parse(stream)

		rawExt = StrS.parse(stream)
		processedExt = StrS.parse(stream)
		subSets_count = stream.read(1)[0]
		subSets = [None] * subSets_count
		for i in range(subSets_count):
			subSets[i] = FilesSubsetS.parse(stream, onthology)

		return FTSMetadata(rawExt, processedExt, subSets)

	@classmethod
	def serialize(cls, self, stream: BytesIO) -> None:
		super(cls, cls).serialize(self, stream)

		StrS.serialize(self.rawExt, stream)
		StrS.serialize(self.processedExt, stream)

		stream.write(bytes((len(self.subSets),)))
		for subSet in self.subSets:
			serialize(subSet, stream)


class OnthArgS(Serializer):

	@classmethod
	def parse(cls, stream):
		iD = stream.read(1)[0]
		typ = ArgType(stream.read(1)[0])
		name = StrS.parse(stream)
		return OnthArg(iD, typ, name)


class OnthologyS(Headered):
	validSignature = "ftsonth"

	@classmethod
	def parse(cls, name, stream):
		super(cls, cls).parse(stream)
		params_count = stream.read(1)[0]
		params = [None] * (params_count)
		for i in range(params_count):
			params[i] = OnthArgS.parse(stream)
		return Onthology(name, params)



class BinaryFormat(IFormat):
	__slots__ = ()

	metaFileExt = "ftsmeta"

	def loadMetadataFile(self, metaFileath: Path):
		return self.parseMetadata(metaFileath.read_bytes())

	def parseMetadata(self, binMetaData: bytes, onthology: None = None) -> ParsedMetadataJSONLikeT:
		with BytesIO(binMetaData) as stream:
			return FTSMetadataS.parse(stream)

	def serializeMetadata(self, loadedMetaFile: FTSMetadata, onthology: None = None) -> bytes:
		if loadedMetaFile.subSets and not onthology:
			raise ValueError("Onthology is required!")

		with BytesIO() as res:
			FTSMetadataS.serialize(loadedMetaFile, res)
			return res.getvalue()

	def dumpMetadataFile(self, metaFileath: Path, meta):
		return metaFileath.write_bytes(self.serializeMetadata(meta))


binaryFormat = BinaryFormat()
