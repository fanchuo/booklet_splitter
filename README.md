# Booklet splitting tool

[![codecov](https://codecov.io/gh/fanchuo/booklet_splitter/branch/master/graph/badge.svg?token=A5DS31YRIC)](https://codecov.io/gh/fanchuo/booklet_splitter)
![Build pass](https://github.com/fanchuo/booklet_splitter/actions/workflows/python-build.yml/badge.svg)

For a given large PDF file, bind a book.

### Installation

On your python environment, just issue this pip install command:
```bash
pip install booklet_splitter
```

### Usage

```bash
usage: booklets [-h] [--max_size MAX_SIZE] [--log LOG] [--targetdir TARGETDIR] [--no-layout] [--cover] input_pdf

For a given pdf, builds booklets to be printed, folded and eventualy assembled as a book

positional arguments:
  input_pdf             PDF file to be sliced as booklets

optional arguments:
  -h, --help            show this help message and exit
  --max_size MAX_SIZE   Max size for a booklet, must be multiple of 4
  --log LOG             Log level at execution
  --targetdir TARGETDIR
                        Directory where the booklets PDF are written
  --no-layout           Only splits your document in booklets
  --cover               Adds a page at the very beginning and at the very end, to paste a cover
```

### Useful commands to print pdf files
For a given pdf, print odd/even pages:
```bash
lpr -o page-set=odd <file>
lpr -o page-set=even <file>
```

For a given pdf, print recto/verso
```bash
lpr -o sides=one-sided <file>
lpr -o sides=two-sided-long-edge <file>
lpr -o sides=two-sided-short-edge <file>
```

Print black and white
```bash
lpr -o saturation=percent <file>
```
