# Booklet splitting tool

[![codecov](https://codecov.io/gh/fanchuo/booklet_splitter/branch/master/graph/badge.svg?token=A5DS31YRIC)](https://codecov.io/gh/fanchuo/booklet_splitter)
![Build pass](https://github.com/fanchuo/booklet_splitter/actions/workflows/python-build.yml/badge.svg)

For a given large PDF file, bind a book.

### Installation

### Usage

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
