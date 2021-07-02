#!/usr/bin/env python3
import sys
import unittest
from collections import OrderedDict
from pathlib import Path

thisDir = Path(__file__).resolve().absolute().parent
repoRootDir = thisDir.parent

sys.path.insert(0, str(repoRootDir))

from fileTestSuite.formats import textFormat, binaryFormat
from fileTestSuite.unittest import FileTestSuiteTestCaseMixin

dict = OrderedDict


class Tests(unittest.TestCase, FileTestSuiteTestCaseMixin):
	__slots__ = ()

	@property
	def fileTestSuiteDir(self) -> Path:
		return thisDir / "testDataset"

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None) -> None:
		chall = challFile.read_text()
		resp = respFile.read_bytes()

		with self.subTest(direction="json2bin"):
			respCand = binaryFormat.serializeMetadata(textFormat.parseMetadata(chall))
			self.assertEqual(resp, respCand)

		with self.subTest(direction="bin2json"):
			challCand = textFormat.serializeMetadata(binaryFormat.parseMetadata(resp))
			self.assertEqual(chall, challCand)


if __name__ == "__main__":
	unittest.main()
