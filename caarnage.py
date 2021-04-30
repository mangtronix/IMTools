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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch

import hashlib

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
        print("  Saving to %s" % screenshotFilename)
        success = self._browser.save_screenshot(screenshotFilename)
        return success

    def getAllScreenshots(self):
        '''Retrieve screenshots for all links'''
        for url in self.highLinks + self.mediumLinks + self.lowLinks:
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
        style = reportlab.lib.styles.getSampleStyleSheet()["Normal"]

        sections = [
            ["High Achievement Examples", self.highLinks],
            ["Medium Achievement Examples", self.mediumLinks],
            ["Low Achievement Examples", self.lowLinks]
        ]

        for description,links in sections:
            p = Paragraph(description, style)

            for link in links:
                print("Adding link %s" % link)
                text = ("URL: %s. " % link)
                p = Paragraph(text, style)
                Story.append(p)
                Story.append(Spacer(1,0.2*inch))

                imageFilename = self.screenshotFilenameForURL(link)
                image = Image(imageFilename)
                image._restrictSize(6 * inch, 4 * inch)
                Story.append(image)

        print("  Building report")
        doc.build(Story,
                    onFirstPage=self.reportTitlePage,
                    onLaterPages=self.reportPage)
        print("  Saved report to %s" % self.reportFilename)

    def reportTitlePage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold',16)
        canvas.drawCentredString(self.reportPageWidth/2.0, self.reportPageHeight-108, self.title)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch,"Page %d" % (doc.page))
        canvas.restoreState()

    def reportPage(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(inch, 0.75 * inch,"Page %d" % (doc.page))
        canvas.restoreState()



    ### Utility functions ###
    def hashForURL(self, url):
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def screenshotFilenameForURL(self, url):
        return self.hashForURL(url) + ".png"




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

def test():
    #testScreenshot()
    #testReport()
    testSmallReport()

if __name__ == "__main__":
    test()
