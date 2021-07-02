import typing
from pathlib import Path

from . import ParsedMetadataJSONLikeT


class IFileNamePairGen:
	__slots__ = ("processedExt",)

	def __init__(self, processedExt: str) -> None:
		self.processedExt = processedExt

	@property
	def challFileGlobPattern(self) -> str:
		raise NotImplementedError

	@property
	def respFileGlobPattern(self):
		return "*." + self.processedExt

	def getChallFileNameFromResp(self, fn: Path):
		raise NotImplementedError

	def globChallFiles(self, subDataSetDir):
		return subDataSetDir.glob(self.challFileGlobPattern)

	def globRespFiles(self, subDataSetDir):
		return subDataSetDir.glob(self.respFileGlobPattern)

	def getChallengeResponseFilePairs(self, subDataSetDir):
		for respFile in self.globRespFiles(subDataSetDir):
			challFile = subDataSetDir / (self.getChallFileNameFromResp(respFile))
			yield challFile, respFile


class FileNamePairGenCompPostfix(IFileNamePairGen):
	__slots__ = ()

	@property
	def challFileGlobPattern(self):
		raise NotImplementedError

	def getChallFileNameFromResp(self, fn: Path):
		return fn.stem


class FileNamePairGenCompReplace(IFileNamePairGen):
	__slots__ = ("rawExt",)

	def __init__(self, processedExt: str, rawExt: str) -> None:
		super().__init__(processedExt)
		self.rawExt = rawExt

	@property
	def challFileGlobPattern(self):
		raise NotImplementedError

	def getChallFileNameFromResp(self, fn: Path) -> str:
		return fn.stem + "." + self.rawExt


class FileNamePairGenCompGlob(FileNamePairGenCompReplace):
	__slots__ = ()

	def getChallFileNameFromResp(self, fn: Path) -> str:
		globbed = tuple(set(fn.parent.glob(super().getChallFileNameFromResp(fn))) - {fn})
		if len(globbed) != 1:
			raise ValueError("Zero/multiple challenge files match the response file", fn, globbed)
		return globbed[0]


def parserGenFactory(parsedMetaFile: ParsedMetadataJSONLikeT) -> FileNamePairGenCompReplace:
	if parsedMetaFile.rawExt:
		if "*" in parsedMetaFile.rawExt:
			return FileNamePairGenCompGlob(parsedMetaFile.processedExt, parsedMetaFile.rawExt)
		else:
			return FileNamePairGenCompReplace(parsedMetaFile.processedExt, parsedMetaFile.rawExt)
	else:
		return FileNamePairGenCompPostfix(parsedMetaFile.processedExt)
