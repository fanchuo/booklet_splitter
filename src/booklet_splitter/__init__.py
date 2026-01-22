"""
For a given large PDF file, this package provides tools
to prepare booklets to bind a book
"""

from typing import List, Dict

from io import open
import pypdf
import logging
from os import makedirs
from pathlib import Path

log = logging.getLogger(__name__)


class BookletSplitterException(Exception):
    """
    Raised if a split parameter is wrong
    """

    pass


class BookletsCollection(object):
    """
    Contains all the output PDF
    """

    def __init__(
        self,
        constituted_booklets: Dict[str, List[pypdf.PageObject]],
        width: float,
        height: float,
    ):
        """
        :param constituted_booklets: Map of booklets, indexed by its filename
        :param width: Page width
        :param height: Page height
        """
        self.constituted_booklets = constituted_booklets
        self.width = width
        self.height = height

    def write_booklets(self, target_directory: str = ".") -> None:
        """
        :param target_directory: Directory where the PDF
            files are to be written
        """
        makedirs(target_directory, exist_ok=True)
        p = Path(target_directory)
        for file_name, pages in self.constituted_booklets.items():
            pdf_writer = pypdf.PdfWriter()
            for page in pages:
                pdf_writer.add_page(page)
            with (p / file_name).open(mode="wb") as out_stream:
                pdf_writer.write(out_stream)
            log.debug(f"Booklet written pdf format : {file_name}")


class PdfHandler(object):
    """
    Analyzer for the large input PDF
    """

    def __init__(self, file: str):
        """
        :param file: PDF file name
        """
        self.file = file

    def __enter__(self):
        self.input_stream = open(self.file, mode="rb")
        self.input_pdf = pypdf.PdfReader(self.input_stream)
        self.num_pages = len(self.input_pdf.pages)
        media_box = self.input_pdf.pages[0].mediabox.upper_right
        self.width = float(media_box[0])
        self.height = float(media_box[1])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.input_stream.close()
