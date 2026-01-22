import logging
from typing import Iterable, List
from booklet_splitter import PdfHandler, BookletsCollection
import pypdf

log = logging.getLogger(__name__)


def generate_volumes(
    input_pdf: str, splits: Iterable[int], target_directory: str = "."
) -> None:
    """
    :param input_pdf: File name of the large PDF to be printed as a book
    :param splits: Page index where to start a new volume
    :param target_directory: Directory where the output PDF will be written
    """
    with PdfHandler(input_pdf) as pdf_handler:
        constituted_booklets = _compute_volumes(pdf_handler, splits)
        constituted_booklets.write_booklets(target_directory)
    log.info("Done")


def _compute_volumes(
    pdf_handler: PdfHandler, splits: Iterable[int]
) -> BookletsCollection:
    """
    :param pdf_handler: Refers input PDF data
    :param splits: Page index where to start a new volume
    :return: A collection of output volumes
    """
    log.info(f"Computed volumes : {splits}")
    page_index = 0
    volume_index = 1
    constituted_booklets = dict()
    s = sorted(splits)
    pages: List[pypdf.PageObject]
    for split in s:
        limit = min(pdf_handler.num_pages, split)
        pages = []
        constituted_booklets["volume{0:02d}.pdf".format(volume_index)] = pages
        while page_index < limit:
            pages.append(pdf_handler.input_pdf.pages[page_index])
            page_index += 1
        volume_index += 1

    pages = []
    constituted_booklets["volume{0:02d}.pdf".format(volume_index)] = pages
    while page_index < pdf_handler.num_pages:
        pages.append(pdf_handler.input_pdf.pages[page_index])
        page_index += 1
    log.info("Volumes splitted")
    return BookletsCollection(
        constituted_booklets, pdf_handler.width, pdf_handler.height
    )
