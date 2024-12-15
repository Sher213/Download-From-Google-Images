import sys
import os
import time
import re
import requests
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

LOAD_PAUSE_TIME = 5
SCROLL_PAUSE_TIME = 5
WEB_PAUSE_TIME = 15

def main(argv):
    #get queries from arguments and umber of images
    numImages = argv[-1]
    queries = argv[:-1]

    if int(numImages) > 400:
        raise Exception("Argument Error: Number is too large. Less Than 400.")

    #build webdriver
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    op.add_argument('--ignore-certificate-errors')
    op.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=op)
    try:
        for query in queries:
            try:
                #This is to get the url for google images w/ selenium
                time.sleep(LOAD_PAUSE_TIME)
                driver.get("https://www.google.com/imghp?hl=en&authuser=0&ogbl")
                #wait for the element
                WebDriverWait(driver, WEB_PAUSE_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'gLFyf')))
                #get element send query and submit
                sBox = driver.find_element(By.CLASS_NAME, 'gLFyf')
                sBox.send_keys(query)
                sBox.send_keys(Keys.ENTER)
                WebDriverWait(driver, WEB_PAUSE_TIME).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'YQ4gaf')))

                # Get scroll height
                last_height = driver.execute_script("return document.body.scrollHeight")

                while True:
                    # Scroll down to bottom
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # Wait to load page
                    time.sleep(SCROLL_PAUSE_TIME)

                    # Calculate new scroll height and compare with last scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                #wait for as many images to load
                time.sleep(WEB_PAUSE_TIME)

                #make directory for images
                path = query
                isExist = os.path.exists(path)
                if not isExist:
                    os.makedirs(path)

                #pass page source to beautiful soup
                soup = BeautifulSoup(driver.page_source, "html.parser")
                images = soup.findAll(class_= 'YQ4gaf')

                for x in range(int(numImages)):

                    #regex to find the src attribute
                    r = re.compile('.*src$')
                    attr = list(filter(r.match, images[x].attrs))
                    src = images[x][attr[0]]

                    #initialize variables
                    img_data, file_ext = '', ''

                    #decode base64 image
                    if 'base64' in src: 
                        head, data = src.split(',', 1)
                        file_ext = '.' + head.split(';')[0].split('/')[1]
                        img_data = base64.b64decode(data)
                    #decode http link
                    elif 'http' in src:
                        r = requests.get(src)
                        img_data = r.content
                        file_ext = '.' + r.headers['Content-Type'].split('/')[1]

                    #write file to correct directory
                    filepath = os.path.join(path, query + str(x) + file_ext)
                    with open(filepath, 'wb') as f:
                        f.write(img_data)

            except Exception as e: 
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(repr(e) + "\nLine No: ", exc_tb.tb_lineno)

        driver.close()
    except Exception as e:
        print(repr(e))

if __name__ == "__main__":
   main(sys.argv[1:])
