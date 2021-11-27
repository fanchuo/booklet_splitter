import logging
from typing import List, Dict
import PyPDF2  # type: ignore
from booklet_splitter import PdfHandler, BookletsCollection, BookletSplitterException

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
        constituted_booklets = _compute_booklets(pdf_handler, cover, max_size)
        if layout:
            _apply_layout(constituted_booklets)
        constituted_booklets.write_booklets(target_directory)
    log.info("Done")


def _compute_booklets(
    pdf_handler: PdfHandler, cover: bool = False, max_size: int = 32
) -> BookletsCollection:
    """
    :param pdf_handler: Refers input PDF data
    :param cover: If True, adds blank pages at the beginning and the end,
        to paste a cover on the book
    :param max_size: Max booklet size
    :return: A collection of output booklets
    """
    if max_size % 4 != 0:
        raise BookletSplitterException(f"max_size = {max_size} is not multiple of 4")
    if max_size <= 0:
        raise BookletSplitterException(
            f"max_size = {max_size} should be strictly positive"
        )
    my_pages = _compute_effective_pages(pdf_handler.num_pages, cover)
    booklets = _compute_booklet_sizes(my_pages, max_size)
    log.info(f"Computed booklets : {booklets}")
    constituted_booklets = _fill_booklets(
        pdf_handler, "booklet{0:02d}.pdf", booklets, cover
    )
    log.info("Booklets splitted")
    return BookletsCollection(
        constituted_booklets, pdf_handler.width, pdf_handler.height
    )


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
    pdf_handler: PdfHandler,
    format_str: str,
    booklets_to_process: List[int],
    cover: bool,
) -> Dict[str, List[PyPDF2.pdf.PageObject]]:
    """
    :param pdf_handler: Refers input PDF data
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
        pages: List[PyPDF2.pdf.PageObject] = []
        booklet_name = format_str.format(booklet_curr)
        constituted_booklets[booklet_name] = pages
        for booklet_idx in range(0, s_booklet):
            if page_idx < 0 or page_idx >= pdf_handler.num_pages:
                pages.append(
                    PyPDF2.pdf.PageObject.createBlankPage(
                        pdf=None, width=pdf_handler.width, height=pdf_handler.height
                    )
                )
            else:
                pages.append(pdf_handler.input_pdf.getPage(page_idx))
            page_idx = page_idx + 1
        booklet_curr = booklet_curr + 1
        log.debug(f"Booklet created : {booklet_name}")
    return constituted_booklets


def _apply_layout(booklets: BookletsCollection) -> None:
    """
    Gives the splitted documents its booklet layout
    :param booklets: Collection of booklets
    """
    _booklet_ordering(booklets)
    _merge(booklets)
    log.info("Printing layout applied")


def _booklet_ordering(booklets: BookletsCollection) -> None:
    """
    Reorders pages to make printable booklets
    :param booklets: Collection of booklets
    """
    for pages in booklets.constituted_booklets.values():
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


def _merge(booklets: BookletsCollection) -> None:
    """
    Merges 2 pages in one
    :param booklets: Collection of booklets
    """
    scale = booklets.width / booklets.height
    for booklet_name, pages in booklets.constituted_booklets.items():
        new_pages = []
        nb_pages = len(pages)
        for rank in range(0, int(nb_pages / 2)):
            blank = PyPDF2.pdf.PageObject.createBlankPage(
                pdf=None, width=booklets.width, height=booklets.height
            )
            page1 = pages[rank * 2]
            page2 = pages[rank * 2 + 1]
            if rank % 2 == 0:
                blank.mergeRotatedScaledTranslatedPage(
                    page1, 90, scale, booklets.width, 0, expand=True
                )
                blank.mergeRotatedScaledTranslatedPage(
                    page2, 90, scale, booklets.width, booklets.height / 2, expand=True
                )
            else:
                blank.mergeRotatedScaledTranslatedPage(
                    page1, -90, scale, 0, booklets.height, expand=True
                )
                blank.mergeRotatedScaledTranslatedPage(
                    page2, -90, scale, 0, booklets.height / 2, expand=True
                )
            new_pages.append(blank)
        pages.clear()
        pages.extend(new_pages)
        log.debug(f"Booklet layout applied : {booklet_name}")
