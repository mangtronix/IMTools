#!/usr/bin/env python

# From https://medium.com/@nikitatonkoshkur25/create-pdf-from-webpage-in-python-1e9603d6a430
#
# Modified to scroll through page to trigger Wordpress lazy load
#
# To install libraries:
# $ pip install webdriver-manager selenium

import base64
import json
import logging
import time
from io import BytesIO
from typing import List

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


class PdfGenerator:
    """
     Simple use case:

        pdf_file = PdfGenerator(['https://google.com']).main()
        with open('new_pdf.pdf', "wb") as outfile:
            outfile.write(pdf_file[0].getbuffer())
    """
    driver = None
    # https://chromedevtools.github.io/devtools-protocol/tot/Page#method-printToPDF
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True,
        'paperWidth': 6.97,
        'paperHeight': 16.5,
    }

    def __init__(self, urls: List[str]):
        self.urls = urls

    def _get_pdf_from_url(self, url, *args, **kwargs):
        # self.driver.implicitly_wait(10)
        self.driver.get(url)
        #time.sleep(5) # Let page HTML load
        self._scroll_page()
        time.sleep(10)  # allow the page to load, increase if needed

        print_options = self.print_options.copy()
        result = self._send_devtools(self.driver, "Page.printToPDF", print_options)
        return base64.b64decode(result['data'])


    '''Scroll page to trigger lazy load images'''
    def _scroll_page(self):
        # Adapted rom https://stackoverflow.com/questions/62600288/how-to-handle-lazy-loaded-images-in-selenium
        print("PdfGenerator: scrolling page")
        SCROLL_PAUSE_TIME = 0.5
        i = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        window_height = self.driver.execute_script("return window.innerHeight");

        # Step through whole page
        print("PDF: scrolling through page")
        current_position = 0
        step = window_height * 0.9 # Step by 90% of window height
        while current_position < last_height:
            self.driver.execute_script("window.scrollTo(0, %d);" % current_position);
            print('.')
            current_position += step
            time.sleep(SCROLL_PAUSE_TIME);

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            i += 1
            if i == 5:
                break

    @staticmethod
    def _send_devtools(driver, cmd, params):
        """
        Works only with chromedriver.
        Method uses cromedriver's api to pass various commands to it.
        """
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        return response.get('value')

    def _generate_pdfs(self):
        pdf_files = []

        for url in self.urls:
            result = self._get_pdf_from_url(url)
            file = BytesIO()
            file.write(result)
            pdf_files.append(file)

        return pdf_files

    def main(self) -> List[BytesIO]:
        webdriver_options = ChromeOptions()
        # webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--disable-gpu')

        try:
            self.driver = webdriver.Chrome(ChromeDriverManager().install(),
                                           options=webdriver_options)
            result = self._generate_pdfs()
        finally:
            self.driver.quit()

        return result

def main():
    pdf_file = PdfGenerator(['https://intro.nyuadim.com/2022/12/14/final-project-documentation-metadrive/']).main()
    with open('test.pdf', "wb") as outfile:
        outfile.write(pdf_file[0].getbuffer())

if __name__ == '__main__':
    main()
