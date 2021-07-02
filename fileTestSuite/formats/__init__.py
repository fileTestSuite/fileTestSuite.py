import typing
from pathlib import Path

from .binary import binaryFormat
from .text import textFormat
from .. import ParsedMetadataJSONLikeT

formatsMatrix = (
	# fromFormat, toFormat
	(textFormat, binaryFormat),
	(binaryFormat, textFormat),
)

sourceExtToPairMapping = {fs[0].metaFileExt: fs for fs in formatsMatrix}

formatsParsingPreference = (textFormat, binaryFormat)


def loadMetadataFile(sourceDir: Path) -> typing.Tuple[ParsedMetadataJSONLikeT, Path]:
	for f in formatsParsingPreference:
		metaFileCand = sourceDir / f.metaFileName
		if metaFileCand.is_file():
			res = f.loadMetadataFile(metaFileCand)
			assert res is not None
			return res, metaFileCand

	return None, None
