import json as jsonFancy
import typing
from pathlib import Path
from collections import OrderedDict

from .core import Serializer
from .. import ParsedMetadataJSONLikeT, FTSMetadata, Parameter, FilesSubset, OnthArg, Onthology
from .core import IFormat

try:
	import mujson as jsonLoad
except ImportError:
	try:
		import ujson as jsonLoad
	except ImportError:
		import json as jsonLoad


class ParameterS(Serializer):

	@classmethod
	def parse(cls, stream):
		iD = stream.read(1)[0]
		size = stream.read(1)[0]
		value = stream.read(size)
		return Parameter(iD, value)

	@classmethod
	def serialize(cls, self, stream):
		stream.write(bytes((self.id, len(self.value))))
		stream.write(self.value)


class FilesSubsetS(Serializer):

	@classmethod
	def parse(cls, jsonParams):
		parameters = []
		for iDStr, v in jsonParams.items():
			iD = onthology.enum[iDStr]
			serializedArg = onthology.types[iD].serialize(v)
			parameters.append(Parameter(iD, serializedArg))
		return parameters

	@classmethod
	def serialize(cls, obj, jso):
		params = {}
		for param in obj.params:
			iD = param.id
			val = param
			if onthology:
				val = onthology[iD].parse(val)

			params[iD] = val
		jso[obj.glob_mask] = params


class FTSMetadataS(Serializer):
	@classmethod
	def parse(cls, jso:ParsedMetadataJSONLikeT) -> "FTSMetadata":
		rawExt = jso["rawExt"]
		processedExt = jso["processedExt"]
		subsets = []

		subSetsJson = jso.get("params", {})
		subSets = FilesSubsetS.parse(subSetsJson)

		return FTSMetadata(rawExt, processedExt, subSets)

	@classmethod
	def serialize(cls, obj: FTSMetadata, jso:ParsedMetadataJSONLikeT) -> None:
		jso["rawExt"] = obj.rawExt
		jso["processedExt"] = obj.processedExt

		if obj.subSets:
			subsetsObj = jso["params"] = {}
			for subSet in obj.subSets:
				self.serialize(subSet, subsetsObj)


class OnthArgS(Serializer):

	@classmethod
	def parse(cls, stream):
		iD = stream.read(1)[0]
		name = stream
		typ = ArgType(stream.read(1)[0])
		return OnthArg(iD, name, typ)


class OnthologyS(Serializer):
	@classmethod
	def parse(cls, name, stream):
		params_count = stream.read(1)[0]
		params = [None] * (params_count)
		for i in range(params_count):
			params[i] = OnthArgS.parse(stream)
		return Onthology(name, params)



class TextFormat(IFormat):
	__slots__ = ()

	metaFileExt = "json"

	def loadMetadataFile(self, metaFilePath: Path) -> ParsedMetadataJSONLikeT:
		return self.parseMetadata(metaFilePath.read_text())

	def parseMetadata(self, metaSource: str) -> ParsedMetadataJSONLikeT:
		parsed = jsonLoad.loads(metaSource, object_pairs_hook=OrderedDict)  # type: ParsedMetadataJSONLikeT
		pm = FTSMetadataS.parse(parsed)
		return pm

	def serializeMetadata(self, meta: ParsedMetadataJSONLikeT) -> str:
		res = OrderedDict()
		FTSMetadataS.serialize(meta, res)
		return jsonFancy.dumps(res, indent="\t")

	def dumpMetadataFile(self, metaFilePath: Path, meta):
		return metaFilePath.write_text(self.serializeMetadata(meta))

textFormat = TextFormat()
