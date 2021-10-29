"""
For a given large PDF file, this package provides tools
to prepare booklets to bind a book
"""
from typing import List, Dict

from io import open
import PyPDF2
import logging
from os import makedirs
from pathlib import Path

log = logging.getLogger(__name__)


def generate_booklets(
    input_pdf: str,
    cover: bool = False,
    layout: bool = True,
    max_size: int = 32,
    target_directory: str = ".",
) -> None:
    """
    :param input_pdf: File name of the large PDF to be printed as a book
    :param cover: Add empty pages at the beginning and the end
        to be able to paste a over on the final book
    :param layout: If True, applies the booklet printing layout to your
        output PDF files
    :param max_size: Maximum size of a booklet
    :param target_directory: Directory where the output PDF will be written
    """
    with PdfHandler(input_pdf) as pdf_handler:
        constituted_booklets = pdf_handler.compute_booklets(cover, max_size)
        if layout:
            constituted_booklets.apply_layout()
        constituted_booklets.write_booklets(target_directory)
    log.info("Done")


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
        constituted_booklets: Dict[str, List[PyPDF2.pdf.PageObject]],
        width: int,
        height: int,
    ):
        """
        :param constituted_booklets: Map of booklets, indexed by its filename
        :param width: Page width
        :param height: Page height
        """
        self.constituted_booklets = constituted_booklets
        self.width = width
        self.height = height

    def apply_layout(self) -> None:
        """
        Gives the splitted documents its booklet layout
        """
        self._booklet_ordering()
        self._merge()
        log.info("Printing layout applied")

    def _booklet_ordering(self) -> None:
        """
        Reorders pages to make printable booklets
        """
        for pages in self.constituted_booklets.values():
            new_pages = []
            nb_pages = len(pages)
            for rank in range(0, int(nb_pages / 2)):
                if rank % 2 == 0:
                    # Recto
                    new_pages.append(pages[nb_pages - 1 - rank])
                    new_pages.append(pages[rank])
                else:
                    # Verso
                    new_pages.append(pages[rank])
                    new_pages.append(pages[nb_pages - 1 - rank])
            pages.clear()
            pages.extend(new_pages)

    def _merge(self) -> None:
        """
        Merges 2 pages in one
        """
        scale = self.width / self.height
        for booklet_name, pages in self.constituted_booklets.items():
            new_pages = []
            nb_pages = len(pages)
            for rank in range(0, int(nb_pages / 2)):
                blank = PyPDF2.pdf.PageObject.createBlankPage(
                    pdf=None, width=self.width, height=self.height
                )
                page1 = pages[rank * 2]
                page2 = pages[rank * 2 + 1]
                if rank % 2 == 0:
                    blank.mergeRotatedScaledTranslatedPage(
                        page1, 90, scale, self.width, 0, expand=True
                    )
                    blank.mergeRotatedScaledTranslatedPage(
                        page2, 90, scale, self.width, self.height / 2, expand=True
                    )
                else:
                    blank.mergeRotatedScaledTranslatedPage(
                        page1, -90, scale, 0, self.height, expand=True
                    )
                    blank.mergeRotatedScaledTranslatedPage(
                        page2, -90, scale, 0, self.height / 2, expand=True
                    )
                new_pages.append(blank)
            pages.clear()
            pages.extend(new_pages)
            log.debug(f"Booklet layout applied : {booklet_name}")

    def write_booklets(self, target_directory: str = ".") -> None:
        """
        :param target_directory: Directory where the PDF
            files are to be written
        """
        makedirs(target_directory, exist_ok=True)
        p = Path(target_directory)
        for file_name, pages in self.constituted_booklets.items():
            pdf_writer = PyPDF2.PdfFileWriter()
            for page in pages:
                pdf_writer.addPage(page)
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
        self.input_pdf = PyPDF2.PdfFileReader(self.input_stream)
        self.num_pages = self.input_pdf.getNumPages()
        media_box = self.input_pdf.getPage(1).mediaBox.upperRight
        self.width = media_box[0]
        self.height = media_box[1]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.input_stream.close()

    def __str__(self):
        return "[PdfHandler - numPages : {0} - width : {1} - height : {2}]".format(
            self.num_pages, self.width, self.height
        )

    def compute_booklets(
        self, cover: bool = False, max_size: int = 32
    ) -> BookletsCollection:
        """
        :param cover: If True, adds blank pages at the beginning and the end,
            to paste a cover on the book
        :param max_size: Max booklet size
        :return: A collection of output booklets
        """
        if max_size % 4 != 0:
            raise BookletSplitterException(
                f"max_size = {max_size} is not multiple of 4"
            )
        if max_size <= 0:
            raise BookletSplitterException(
                f"max_size = {max_size} should be strictly positive"
            )
        log.info(self)
        my_pages = self._compute_effective_pages(self.num_pages, cover)
        booklets = self._compute_booklet_sizes(my_pages, max_size)
        log.info(f"Computed booklets : {booklets}")
        constituted_booklets = self._fill_booklets(
            "booklet{0:02d}.pdf", booklets, cover
        )
        log.info("Booklets splitted")
        return BookletsCollection(constituted_booklets, self.width, self.height)

    @staticmethod
    def _compute_effective_pages(pages: int, cover: bool) -> int:
        """
        :param pages: Actual number of pages in this large input PDF
        :param cover: If True, adds blank pages at the beginning and the end
            of the book to paste a cover
        :return: Cumulated number of pages for the booklets
        """
        to_return = pages
        if cover:
            to_return += 4
        while to_return % 4 != 0:
            to_return = to_return + 1
        return to_return

    @staticmethod
    def _compute_booklet_sizes(effective_pages: int, max_size: int) -> List[int]:
        """
        :param effective_pages: Total number of pages,
            computed for all the booklets
        :param max_size: Max booklet size
        :return: The list of booklets sizes to be used for split
        """
        min_size = ((max_size // 2) // 4) * 4
        if min_size > 0:
            min_size -= 1
        log.debug(f"Computed min size : {min_size}")

        for b_size in range(max_size, min_size, -4):
            nb_booklets = effective_pages // b_size
            rest = effective_pages % b_size
            if rest == 0:
                return [b_size] * nb_booklets
            adjust = (b_size - rest) // 4
            if adjust <= nb_booklets:
                large_booklets = 1 + (nb_booklets - adjust)
                return [b_size] * large_booklets + [b_size - 4] * adjust
        return [effective_pages]

    def _fill_booklets(
        self, format_str: str, booklets_to_process: List[int], cover: bool
    ) -> Dict[str, List[PyPDF2.pdf.PageObject]]:
        """
        :param format_str: Template for the booklet name
        :param booklets_to_process: Sizes computed for booklets
        :param cover: If True, adds blank page at the beginning
            and the end to paste a cover
        :return: Map of booklets, indexed by its name
        """
        if cover:
            page_idx = -2
        else:
            page_idx = 0
        booklet_curr = 1
        constituted_booklets = {}
        for s_booklet in booklets_to_process:
            pages = []
            booklet_name = format_str.format(booklet_curr)
            constituted_booklets[booklet_name] = pages
            for booklet_idx in range(0, s_booklet):
                if page_idx < 0 or page_idx >= self.num_pages:
                    pages.append(
                        PyPDF2.pdf.PageObject.createBlankPage(
                            pdf=None, width=self.width, height=self.height
                        )
                    )
                else:
                    pages.append(self.input_pdf.getPage(page_idx))
                page_idx = page_idx + 1
            booklet_curr = booklet_curr + 1
            log.debug(f"Booklet created : {booklet_name}")
        return constituted_booklets
