from pathlib import Path
from sys import stderr

from plumbum import cli

from .formats import sourceExtToPairMapping
from .formats.text import textFormat

DEFAULT_FILE = Path("./" + textFormat.metaFileName)


class MainCLI(cli.Application):
	pass


@MainCLI.subcommand("convert")
class CompilerCLI(cli.Application):
	"""Converts between human-editable and machine-readable variants of the spec"""

	def main(self, inputFilePath: cli.switches.ExistingFile = DEFAULT_FILE):
		inputFilePath = Path(inputFilePath)
		fromFormat, toFormat = sourceExtToPairMapping[inputFilePath.suffix[1:]]
		outputFilePath = inputFilePath.parent / (inputFilePath.stem + "." + toFormat.metaFileExt)
		print("Converting from", inputFilePath.name,  "to", outputFilePath.name, file=stderr)

		parsedMetaFile = fromFormat.loadMetadataFile(inputFilePath)
		toFormat.dumpMetadataFile(outputFilePath, parsedMetaFile)

@MainCLI.subcommand("init")
class InitCLI(cli.Application):
	"""Populates the default template"""

	def main(self):
		from .template import TEMPLATE

		fP = DEFAULT_FILE
		textFormat.dumpMetadataFile(fP, TEMPLATE)


if __name__ == "__main__":
	MainCLI.run()
