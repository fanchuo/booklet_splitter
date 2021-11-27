import unittest
import importlib.resources
from .. import resources
from booklet_splitter import booklets, volumes, grayscale
from tempfile import TemporaryDirectory
import logging
from os import listdir
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.INFO)
with importlib.resources.path(resources, "test.pdf") as contents:
    pdf_path = str(contents)


def analyze_split(tmp: str) -> str:
    split_result = ""
    for pdf in sorted(listdir(tmp)):
        split_result += pdf + "\n"
        output = subprocess.getoutput(f"pdftotext -layout {Path(tmp)/pdf} -")
        output = "".join([c for c in output if c != "\f"])
        split_result += output + "\n"
    return split_result.strip()


class TestBookletSplitter(unittest.TestCase):
    def test_simple(self):
        with TemporaryDirectory() as tmp:
            booklets.generate_booklets(input_pdf=pdf_path, target_directory=str(tmp))
            split_result = analyze_split(tmp)

        self.assertEqual(
            split_result,
            """booklet01.pdf
1
2
10   3
4   9
8   5
6   7""",
        )

    def test_2booklets(self):
        with TemporaryDirectory() as tmp:
            booklets.generate_booklets(
                input_pdf=pdf_path, target_directory=str(tmp), max_size=8
            )
            split_result = analyze_split(tmp)

        self.assertEqual(
            split_result,
            """booklet01.pdf
8   1
2   7
6   3
4   5

booklet02.pdf
9
10""",
        )

    def test_cover(self):
        with TemporaryDirectory() as tmp:
            booklets.generate_booklets(
                input_pdf=pdf_path, target_directory=str(tmp), max_size=8, cover=True
            )
            split_result = analyze_split(tmp)

        self.assertEqual(
            split_result,
            """booklet01.pdf
6
5
4   1
2   3

booklet02.pdf
7
8
9
10""",
        )

    def test_layout(self):
        with TemporaryDirectory() as tmp:
            booklets.generate_booklets(
                input_pdf=pdf_path, target_directory=str(tmp), layout=False
            )
            split_result = analyze_split(tmp)

        self.assertEqual(
            split_result,
            """booklet01.pdf
1
2
3
4
5
6
7
8
9
10""",
        )

    def test_volumes(self):
        with TemporaryDirectory() as tmp:
            volumes.generate_volumes(
                input_pdf=pdf_path, target_directory=str(tmp), splits=[4]
            )
            split_result = analyze_split(tmp)

        self.assertEqual(
            split_result,
            """volume01.pdf
1
2
3
4

volume02.pdf
5
6
7
8
9
10""",
        )

    def test_grayscale(self):
        with TemporaryDirectory() as tmp:
            out = str(Path(tmp) / "output.pdf")
            grayscale.grayscale(input_pdf=pdf_path, output_pdf=out)
            split_result = analyze_split(tmp)

        self.assertEqual(
            split_result,
            "output.pdf",
        )

    @unittest.expectedFailure
    def test_not_multiple4(self):
        with TemporaryDirectory() as tmp:
            booklets.generate_booklets(
                input_pdf=pdf_path, target_directory=str(tmp), max_size=7
            )

    @unittest.expectedFailure
    def test_not_positive(self):
        with TemporaryDirectory() as tmp:
            booklets.generate_booklets(
                input_pdf=pdf_path, target_directory=str(tmp), max_size=0
            )
