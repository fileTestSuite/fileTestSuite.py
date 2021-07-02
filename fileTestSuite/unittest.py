import sys
import unittest
from os import environ
from pathlib import Path

from .FileNamePairGen import parserGenFactory
from .formats import loadMetadataFile

SHOULD_TRACE = int(environ.get("FILE_TEST_SUITE_TRACING", 0))


class FileTestSuiteTestCaseMixin:
	__slots__ = ()

	@property
	def fileTestSuiteDir(self):
		raise NotImplementedError

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None):
		raise NotImplementedError

	def _testImplodeDecoderForASubDataSet(self, subDataSetDir: Path, metaData):
		fnpg = parserGenFactory(metaData)
		for challFile, respFile in fnpg.getChallengeResponseFilePairs(subDataSetDir):
			with self.subTest(chall=challFile.stem):
				self._testProcessorImpl(challFile, respFile, paramsDict=None)

	def testUsingDataset(self):
		if SHOULD_TRACE:
			cwd = Path(".").absolute()

		for subDataSetDir in self.fileTestSuiteDir.iterdir():
			if SHOULD_TRACE:
				print("subDataSetDir", subDataSetDir.relative_to(cwd), subDataSetDir.is_dir(), file=sys.stderr)
			if subDataSetDir.is_dir():
				metaData, metaDataFile = loadMetadataFile(subDataSetDir)
				if SHOULD_TRACE:
					print("Metadata file found:", metaDataFile.relative_to(cwd), file=sys.stderr)
					print("Metadata:", metaData, file=sys.stderr)
				if metaData:
					with self.subTest(dataset=subDataSetDir.name, metaData=metaData, metaDataFile=metaDataFile):
						self._testImplodeDecoderForASubDataSet(subDataSetDir, metaData)
