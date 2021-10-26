from typing import List, Dict

from io import open
import PyPDF2

def compute_effective_pages(pages: int, cover: bool) -> int:
    to_return = pages
    if cover:
        to_return += 4
    while to_return % 4 != 0:
        to_return = to_return + 1
    return to_return


def compute_booklets(effective_pages: int, min_size: int, max_size: int) -> List[int]:
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


def booklet_ordering(constituted_booklets: Dict[str, List[PyPDF2.pdf.PageObject]]) -> None:
    for pages in constituted_booklets.values():
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


class PdfHandler(object):
    def __init__(self, file):
        self.inputStream = open(file, mode='rb')
        self.inputPdf = PyPDF2.PdfFileReader(self.inputStream)
        self.numPages = self.inputPdf.getNumPages()
        media_box = self.inputPdf.getPage(1).mediaBox.upperRight
        self.width = media_box[0]
        self.height = media_box[1]

    def __str__(self):
        return '[PdfHandler - numPages : {0} - width : {1} - height : {2}]' \
            .format(self.numPages, self.width, self.height)

    def close(self):
        self.inputStream.close()

    def fill_booklets(self, format_str: str, booklets_to_process: List[int], cover: bool) -> Dict[
        str, List[PyPDF2.pdf.PageObject]]:
        if cover:
            page_idx = -2
        else:
            page_idx = 0
        booklet_curr = 1
        constituted_booklets = {}
        for s_booklet in booklets_to_process:
            pages = []
            constituted_booklets[format_str.format(booklet_curr)] = pages
            for booklet_idx in range(0, s_booklet):
                if page_idx < 0 or page_idx >= self.numPages:
                    pages.append(PyPDF2.pdf.PageObject.createBlankPage(pdf=None, width=self.width, height=self.height))
                else:
                    pages.append(self.inputPdf.getPage(page_idx))
                page_idx = page_idx + 1
            booklet_curr = booklet_curr + 1
        return constituted_booklets

    def merge(self, constituted_booklets: Dict[str, List[PyPDF2.pdf.PageObject]]) -> None:
        scale = self.width / self.height
        for pages in constituted_booklets.values():
            new_pages = []
            nb_pages = len(pages)
            for rank in range(0, int(nb_pages / 2)):
                blank = PyPDF2.pdf.PageObject.createBlankPage(pdf=None, width=self.width, height=self.height)
                page1 = pages[rank * 2]
                page2 = pages[rank * 2 + 1]
                if rank % 2 == 0:
                    blank.mergeRotatedScaledTranslatedPage(page1, 90, scale, self.width, 0, expand=True)
                    blank.mergeRotatedScaledTranslatedPage(page2, 90, scale, self.width, self.height / 2, expand=True)
                else:
                    blank.mergeRotatedScaledTranslatedPage(page1, -90, scale, 0, self.height, expand=True)
                    blank.mergeRotatedScaledTranslatedPage(page2, -90, scale, 0, self.height / 2, expand=True)
                new_pages.append(blank)
            pages.clear()
            pages.extend(new_pages)

    def write_booklets(self, constituted_booklets: Dict[str, List[PyPDF2.pdf.PageObject]]) -> None:
        for file_name, pages in constituted_booklets.items():
            pdf_writer = PyPDF2.PdfFileWriter()
            for page in pages:
                if page:
                    pdf_writer.addPage(page)
                else:
                    pdf_writer.addBlankPage(self.width, self.height)
            out_stream = open(file_name, mode='wb')
            pdf_writer.write(out_stream)
            out_stream.close()
