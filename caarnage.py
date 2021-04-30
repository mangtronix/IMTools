#!/usr/bin/python

# Generate an assessment report for CAaR
# Michael Ang
# https://github.com/mangtronix/
# https://michaelang.com
#
# MIT License

from selenium import webdriver

class Assessment:

    def __init__(self):
        self.title = 'Assessment'
        self.description = 'Assessment description'

        self.highLinks = []
        self.mediumLinks = []
        self.lowLinks = []

        self.reportFilename = 'assessment.pdf'

        self._browser = None

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

    def quitBrowser(self):
        if self._browser is not None:
            self._browser.quit()

    def shutdown(self):
        self.quitBrowser()



def test():
    assessment = Assessment()
    assessment.makeScreenshot('https://lucychoi1215.github.io/actors.html', 'actors.png')
    assessment.shutdown()

if __name__ == "__main__":
    test()
