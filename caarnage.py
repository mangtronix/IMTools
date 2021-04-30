#!/usr/bin/python

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

from selenium import webdriver

import reportlab
import reportlab.rl_config, reportlab.lib.styles
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.units import inch

import hashlib
import os
import PIL

'''Add links and then generate a PDF'''
class Assessment:

    def __init__(self):
        self.title = 'Assessment'
        self.description = 'Assessment description'

        self.highLinks = []
        self.mediumLinks = []
        self.lowLinks = []

        self._browser = None

        # Report settings
        self.reportFilename = 'assessment.pdf'
        self.reportPageHeight = reportlab.rl_config.defaultPageSize[0]
        self.reportPageWidth = reportlab.rl_config.defaultPageSize[1]

        self.screenshotDirectory = 'screenshots'
        if not os.path.isdir(self.screenshotDirectory):
            os.mkdir(self.screenshotDirectory)


    def initBrowser(self):
        if self._browser is not None:
            self._browser.quit()

        print("Initializing browser")
        self._browser = webdriver.Firefox()

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
            filename = self.screenshotFilenameForURL(url)
            if useCached:
                if self.fileHasData(filename):
                    print("  Already have screenshot for %s, skipping"  % url)
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
        Story = [Spacer(1,2*inch)]
        headingStyle = reportlab.lib.styles.getSampleStyleSheet()["Heading1"]
        normalStyle = reportlab.lib.styles.getSampleStyleSheet()["Normal"]

        sections = [
            ["High Achievement Examples", self.highLinks],
            ["Medium Achievement Examples", self.mediumLinks],
            ["Low Achievement Examples", self.lowLinks]
        ]

        p = Paragraph(self.title, headingStyle)
        Story.append(p)
        p = Paragraph(self.description, normalStyle)
        Story.append(p)
        Story.append(PageBreak())


        for description,links in sections:
            if len(links) < 1:
                print("  No links in section: %s" % description)
                continue

            p = Paragraph(description, headingStyle)
            Story.append(p)

            for link in links:
                print("Adding link %s" % link)
                text = ("URL: %s " % link)
                p = Paragraph(text, normalStyle)

                imageFilename = self.screenshotFilenameForURL(link)
                image = Image(imageFilename)
                image._restrictSize(6 * inch, 4 * inch)

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

def test():
    #testScreenshot()
    #testReport()
    #testSmallReport()
    testMediumReport()

if __name__ == "__main__":
    test()
