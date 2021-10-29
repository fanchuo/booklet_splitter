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

Install pdftotext and pdfseparate utilities
```bash
apt install poppler-utils
```

Obtain coverage tests reports:
```bash
coverage run setup.py test
coverage report
coverage html
```

Dev mode:
```bash
pip install -e .[tests]
```
