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

I make a new config file for each assessment. Here's an example file:
example.yaml
```
title: Assessment 1 - Webpage Assignment
description: Examples of the submitted webpages follow
filename: example.pdf
high:
  - https://lucychoi1215.github.io/
medium:
  - https://github.com/NYUAD-IM/Software-Art-Image/tree/main/code/velocity
low:
  - https://github.com/NYUAD-IM/Software-Art-Image/tree/main/code/simpletimeline
  - https://github.com/NYUAD-IM/Software-Art-Image/tree/main/code/grid
```

Then run CAaRnage like so:
```
$ ./caarnage example.yaml
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
