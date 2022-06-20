# IMTools
Possibly maybe useful tools for NYUAD Interactive Media

## CAaRnage
CAaRnage can generate a PDF that contains example work from a list of URLs.

To set the report options, edit ```config.yaml```. Then run ```caarnage.py```.

To install the required Python modules using Conda

```
$ conda config --append channels conda-forge
$ conda install --file requirements.txt
```

## Making a PDF of a GitHub repository

Because the CAaR system won't accept a zip file.

Install wkhtmltopdf
* https://github.com/pdfkit/PDFKit/wiki/Installing-WKHTMLTOPDF
* ```$ brew install --cask wkhtmltopdf```

Install code2pdf
* https://github.com/lucascaton/code2pdf
* ```$ gem install code2pdf```

Generate pdf
* ```$ code2pdf {repo directory}```
