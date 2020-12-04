#!/usr/bin/env python3

from io import open
from sys import argv
import PyPDF2


class BookletSplitter(object):
    @staticmethod
    def effective_pages(pages):
        to_return = pages + 4
        while to_return % 4 != 0:
            to_return = to_return + 1
        return to_return

    @staticmethod
    def compute_booklets(effective_pages):
        for b_size in (32, 28, 24, 20, 16):
            nb_booklets = effective_pages // b_size
            rest = effective_pages % b_size
            if rest == 0:
                return [b_size] * nb_booklets
            adjust = (b_size - rest) // 4
            if adjust <= nb_booklets:
                large_booklets = 1 + (nb_booklets-adjust)
                return [b_size] * large_booklets + [b_size-4] * adjust
        return []

    @staticmethod
    def booklet_ordering(constituted_booklets):
        for pages in constituted_booklets.values():
            new_pages = []
            nbPages = len(pages)
            for rank in range(0, int(nbPages/2)):
                if rank%2 == 0:
                    # Recto
                    new_pages.append(pages[nbPages-1-rank])
                    new_pages.append(pages[rank])
                else:
                    # Verso
                    new_pages.append(pages[rank])
                    new_pages.append(pages[nbPages-1-rank])
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
        return '[PdfHandler - numPages : {0} - width : {1} - height : {2}]'\
            .format(self.numPages, self.width, self.height)

    def close(self):
        self.inputStream.close()

    def fill_booklets(self, format_str, booklets_to_process):
        page_idx = -2
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

    def merge(self, constituted_booklets):
        scale = self.width/self.height
        for pages in constituted_booklets.values():
            new_pages = []
            nbPages = len(pages)
            for rank in range(0, int(nbPages/2)):
                blank = PyPDF2.pdf.PageObject.createBlankPage(pdf=None, width=self.width, height=self.height)
                page1 = pages[rank*2]
                page2 = pages[rank*2 + 1]
                if rank%2 == 0:
                    blank.mergeRotatedScaledTranslatedPage(page1, 90, scale, self.width, 0, expand=True)
                    blank.mergeRotatedScaledTranslatedPage(page2, 90, scale, self.width, self.height/2, expand=True)
                else:
                    blank.mergeRotatedScaledTranslatedPage(page1, -90, scale, 0, self.height, expand=True)
                    blank.mergeRotatedScaledTranslatedPage(page2, -90, scale, 0, self.height/2, expand=True)
                new_pages.append(blank)
            pages.clear()
            pages.extend(new_pages)
        

    def write_booklets(self, constituted_booklets):
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


if __name__ == '__main__':
    input_pdf = PdfHandler(argv[1])
    print(input_pdf)
    myPages = BookletSplitter.effective_pages(input_pdf.numPages)
    print(myPages)
    booklets = BookletSplitter.compute_booklets(myPages)
    print(booklets)
    constituted_booklets = input_pdf.fill_booklets('booklet{0:02d}.pdf', booklets)
    #print(contituted_booklets)
    BookletSplitter.booklet_ordering(constituted_booklets)
    input_pdf.merge(constituted_booklets)
    input_pdf.write_booklets(constituted_booklets)
