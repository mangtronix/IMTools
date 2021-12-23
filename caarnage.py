#!/usr/bin/env python

# Generate an assessment report for CAaR
# Michael Ang
# https://github.com/mangtronix/
# https://michaelang.com
#
# MIT License

# Dependencies
# - selenium
# - geckodriver
# - reportlab
# - platypus

# To install the dependencies using Conda
# $ conda config --append channels conda-forge
# $ conda install --file requirements.txt

# TODO:
# - add option to save page to pdf (https://stackoverflow.com/questions/59893671/pdf-printing-from-selenium-with-chromedriver)
# - clone GitHub repositories

from selenium import webdriver

import reportlab
import reportlab.rl_config, reportlab.lib.styles
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.units import inch

import hashlib
import os, sys
import PIL
import yaml

from optparse import OptionParser

'''Add links and then generate a PDF'''
class Assessment:

    def __init__(self, yamlConfigFilename = None):
        self.title = 'Assessment'
        self.description = 'Assessment description'

        self.highDescription = ''
        self.highLinks = []

        self.mediumDescription = ''
        self.mediumLinks = []

        self.lowDescription = ''
        self.lowLinks = []

        self._browser = None
        self._browserWaitTime = 10 # Implicit wait
        self.screenshotWidth = 1920
        self.screenshotHeight = 1200

        # Report settings
        self.reportFilename = 'assessment.pdf'
        self.reportPageHeight = reportlab.rl_config.defaultPageSize[0]
        self.reportPageWidth = reportlab.rl_config.defaultPageSize[1]

        self.screenshotDirectory = 'screenshots'

        if yamlConfigFilename is not None:
            self.updateFromConfig(yamlConfigFilename)

        if not os.path.isdir(self.screenshotDirectory):
            os.mkdir(self.screenshotDirectory)

    def initBrowser(self):
        if self._browser is not None:
            self._browser.quit()

        print("Initializing browser")
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--width=%d" % self.screenshotWidth)
        opts.add_argument("--height=%d" % self.screenshotHeight)
        self._browser = webdriver.Firefox(options = opts)
        self._browser.implicitly_wait(self._browserWaitTime)

    def updateFromConfig(self, yamlFilename):
        with open(yamlFilename) as file:
            documents = yaml.full_load(file)

        for item, doc in documents.items():
            if item == 'title':
                self.title = doc
            elif item == 'description':
                self.description = doc
            elif item == 'filename':
                self.reportFilename = doc
            elif item == 'high':
                self.highLinks = doc
            elif item == 'medium':
                self.mediumLinks = doc
            elif item == 'low':
                self.lowLinks = doc
            elif item == 'high_description':
                self.highDescription = doc
            elif item == 'medium_description':
                self.mediumDescription = doc
            elif item == 'low_description':
                self.lowDescription = doc
            elif item == 'screenshot_width':
                self.screenshotWidth = doc
            elif item == 'screenshot_height':
                self.screenshotHeight = doc

    def printConfig(self):
        print("Title: " + self.title)
        print("Description: " + self.description)
        print("Filename: " + self.reportFilename)
        print("Screenshot size: %dx%d" % (self.screenshotWidth, self.screenshotHeight))
        print("High description: %s" % self.highDescription)

        print("High Achievement URLs:")
        for url in self.highLinks:
            print("  %s" % url)

        print("Medium description: %s" % self.mediumDescription)
        print("Medium Achievement URLs:")
        for url in self.mediumLinks:
            print("  %s" % url)

        print("Low description: %s" % self.lowDescription)
        print("Low Achievement URLs:")
        for url in self.lowLinks:
            print("  %s" % url)

    def makeScreenshot(self, url, screenshotFilename):
        if self._browser is None:
            self.initBrowser()

        print("Getting %s" % url)
        self._browser.get(url)

        pngFilename = self.screenshotBasenameForURL(url) + '.png'
        print("  Saving to %s" % pngFilename)
        success = self._browser.save_screenshot(pngFilename)

        if success:
            print("  Converting to jpg")
            im = PIL.Image.open(pngFilename)
            im.convert('RGB').save(screenshotFilename)
            os.remove(pngFilename)

        return success

    def getAllScreenshots(self, useCached = True):
        '''Retrieve screenshots for all links'''
        print("Getting screenshots")
        for url in self.highLinks + self.mediumLinks + self.lowLinks:
            if url is None:
                print("  Empty URL, skipping")
                continue
            filename = self.screenshotFilenameForURL(url)
            if useCached:
                if self.fileHasData(filename):
                    print("  Already have screenshot for %s, using cached version"  % url)
                    continue
            self.makeScreenshot(url, self.screenshotFilenameForURL(url))


    def quitBrowser(self):
        if self._browser is not None:
            self._browser.quit()

    def shutdown(self):
        self.quitBrowser()


    def buildReport(self):
        print("Generating report to %s" % self.reportFilename)
        doc = SimpleDocTemplate(self.reportFilename)
        Story = [Spacer(1,1*inch)]
        headingStyle = reportlab.lib.styles.getSampleStyleSheet()["Heading1"]
        normalStyle = reportlab.lib.styles.getSampleStyleSheet()["Normal"]

        sections = [
            ["High Achievement Examples", self.highLinks, self.highDescription],
            ["Medium Achievement Examples", self.mediumLinks, self.mediumDescription],
            ["Low Achievement Examples", self.lowLinks, self.lowDescription]
        ]

        p = Paragraph(self.title, headingStyle)
        Story.append(p)
        p = Paragraph(self.description, normalStyle)
        Story.append(p)
        Story.append(PageBreak())


        for title,links,description in sections:
            if len(links) < 1:
                print("  No links in section: %s" % description)
                continue

            p = Paragraph(title, headingStyle)
            Story.append(p)

            if description:
                p = Paragraph(description, normalStyle)
                Story.append(p)
                Story.append(Spacer(1,0.25*inch))

            for link in links:
                if link is None:
                    continue
                print("Adding link %s" % link)
                text = "URL: <a href='%s'>%s</a>" % (link, link)
                #text = "URL: %s" % link
                p = Paragraph(text, normalStyle)

                imageFilename = self.screenshotFilenameForURL(link)
                image = Image(imageFilename)
                image._restrictSize(7 * inch, 5 * inch)

                Story.append(KeepTogether([p, image]))
                Story.append(Spacer(1,0.2*inch))

            Story.append(PageBreak())

        print("  Building report")
        doc.build(Story,
                    onFirstPage=self.reportPage,
                    onLaterPages=self.reportPage)
        print("  Saved report to %s" % self.reportFilename)

    # def reportTitlePage(self, canvas, doc):
    #     print("Making title page")
    #     canvas.saveState()
    #     canvas.setFont('Times-Bold',16)
    #     canvas.drawCentredString(self.reportPageWidth/2.0, self.reportPageHeight-108, self.title)
    #     canvas.setFont('Times-Roman',9)
    #     canvas.drawString(inch, 0.75 * inch,"Page %d" % (doc.page))
    #     canvas.restoreState()

    def reportPage(self, canvas, doc):
        print("Making page %d" % doc.page)
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(inch, 0.75 * inch,"Page %d" % (doc.page))
        canvas.restoreState()



    ### Utility functions ###
    def hashForURL(self, url):
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def screenshotBasenameForURL(self, url):
        return os.path.join(self.screenshotDirectory, self.hashForURL(url))

    def screenshotFilenameForURL(self, url):
        return self.screenshotBasenameForURL(url) + '.jpg'

    def fileHasData(self, filename):
        return os.path.isfile(filename) and os.path.getsize(filename) > 0

    def doItAll(self):
        self.printConfig()
        self.getAllScreenshots()
        self.quitBrowser()
        self.buildReport()
        self.shutdown()


##### COMMAND LINE
def go():
    defaultConfig = 'config.yaml'

    usage = "usage: %prog config1.yaml config2.yaml ..."

    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        printHelp()
        print("Using default config file %s" % defaultConfig)
        args = [defaultConfig]

    for config in args:
        assessment = Assessment(config)
        assessment.doItAll()

def printHelp():
    print("caarnage.py config.yml")
    print()
    print("Edit the default config file config.yml to set the report options")


##### TESTING

def testScreenshot():
    print("Testing screenshot")
    assessment = Assessment()
    assessment.makeScreenshot('https://lucychoi1215.github.io/actors.html', 'actors.png')
    assessment.shutdown()

def testReport():
    print("Testing report")
    assessment = Assessment()
    assessment.buildReport()
    assessment.shutdown()

def testSmallReport():
    print("Testing small report")
    assessment = Assessment()
    assessment.reportFilename = 'smallreport.pdf'
    assessment.highLinks.append('https://lucychoi1215.github.io/actors.html')
    assessment.getAllScreenshots()
    assessment.buildReport()
    assessment.shutdown()

def testMediumReport():
    print("Testing medium report")
    assessment = Assessment()
    assessment.title = "Assessments for Assignment 1"
    assessment.description = "Examples of the websites submitted for Assignment 1 follow, with URLs to the sites and screenshots."
    assessment.reportFilename = 'mediumreport.pdf'
    assessment.highLinks.extend([
        'https://lucychoi1215.github.io/',
        'https://lucychoi1215.github.io/actors.html',
        'https://lucychoi1215.github.io/about.html'
    ])

    assessment.mediumLinks.extend([
        'https://martapienkosz.github.io/30mff/',
        'https://martapienkosz.github.io/30mff/#about',
        'https://martapienkosz.github.io/30mff/#actors'
    ])

    assessment.lowLinks.extend([
        'http://zharmakhan-zn.github.io/',
        'https://zharmakhan-zn.github.io/video.html',
        'https://zharmakhan-zn.github.io/crew.html'
    ])

    assessment.getAllScreenshots()
    assessment.buildReport()
    assessment.shutdown()

def testConfig():
    assessment = Assessment()
    assessment.updateFromConfig('example.yaml')
    assessment.printConfig()
    assessment.getAllScreenshots()
    assessment.buildReport()
    assessment.shutdown()

def test():
    #testScreenshot()
    #testReport()
    #testSmallReport()
    #testMediumReport()
    testConfig()

if __name__ == "__main__":
    go()
