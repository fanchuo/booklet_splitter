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

    def write_booklets(self, format_str, booklets_to_process):
        page_idx = -2
        booklet_curr = 1
        for s_booklet in booklets_to_process:
            pdf_writer = PyPDF2.PdfFileWriter()
            for booklet_idx in range(0, s_booklet):
                if page_idx < 0 or page_idx >= self.numPages:
                    pdf_writer.addBlankPage(self.width, self.height)
                else:
                    pdf_writer.addPage(self.inputPdf.getPage(page_idx))
                page_idx = page_idx + 1
            out_stream = open(format_str.format(booklet_curr), mode='wb')
            pdf_writer.write(out_stream)
            out_stream.close()
            booklet_curr = booklet_curr + 1


if __name__ == '__main__':
    input_pdf = PdfHandler(argv[1])
    print(input_pdf)
    myPages = BookletSplitter.effective_pages(input_pdf.numPages)
    print(myPages)
    booklets = BookletSplitter.compute_booklets(myPages)
    print(booklets)
    input_pdf.write_booklets('booklet{0:02d}.pdf', booklets)
