from lib2to3.pgen2 import driver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import text_processing
import electoral_pdf
import pdf
import db
import image_processing
import pdf
import voter_info

import re
import os
import time


def get_driver(pdf_path=os.path.join(os.getcwd(), "tmp", "pdf")):

    option = Options()
    # option.set_preference("browser.download.folderList", 2)
    # option.set_preference("browser.download.manager.showWhenStarting", False)
    # option.set_preference("browser.download.dir", pdf_path)
    # option.set_preference(
    #     "browser.download.viewableInternally.enabledTypes", "")
    # option.set_preference("browser.helperApps.neverAsk.saveToDisk",
    #                       "application/octet-stream,application/pdf")
    # option.set_preference("pdfjs.enabledCache.state", False)

    option.add_experimental_option('prefs', {
        # Change default directory for downloads
        "download.default_directory": pdf_path,
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        # It will not show PDF directly in chrome
        "plugins.always_open_pdf_externally": True
    })

    #option.set_preference("pdfjs.disabled", True)
    #option.set_preference("plugin.scan.Acrobat", "99.0")
    #option.set_preference("plugin.scan.plid.all", False)

    option.headless = False

    driverPath = os.path.join(os.getcwd(), "driver", "chromedriver")
    driver = webdriver.Chrome(options=option, executable_path=driverPath)

    return driver


def handle_electoral_pdf_scrape(db_client, req):
    p = os.path.join(os.getcwd(), "tmp", "pdf")
    driver = get_driver(pdf_path=p)

    try:
        state = text_processing.rm_spaces(req['state'].lower())
        ac = text_processing.rm_spaces(req['ac'])
        pc = text_processing.rm_spaces(req['pc'])
        part_no = text_processing.rm_spaces(req['part_no'])
        part_name = text_processing.rm_spaces(req['part_name'])

        if re.match(r".*uttar.*pradesh.*", state):
            electoral_pdf.get_uttar_pradesh_by_data(driver, req)
            ocr_lang = "Devanagari"
            lang_src = "hi"

        elif re.match(r".*tamil.*nadu.*", state):
            electoral_pdf.get_tamil_nadu_by_data(driver, req)
            ocr_lang = "Tamil"
            lang_src = "ta"

        else:
            raise Exception('no scraper for state')

        fname = os.listdir(p)[0]
        pdf_f = os.path.join(p, fname)
        images = pdf.pdf_as_image_crops(pdf_f)
        os.remove(pdf_f)

        print("scrape-pdf: extacting pdf data")

        bulk_data = []
        for m1, m2 in images:
            t1 = image_processing.image_to_text(m1, lang=ocr_lang)
            t1 = list(
                map(lambda x: text_processing.rm_special_characters(x), t1.split('\n')))
            t1 = list(map(lambda x: text_processing.rm_spaces(x), t1))
            t1 = '\n'.join(t1)

            if not t1:
                continue

            # epic number
            t2 = image_processing.image_to_text(m2)

            en_t = text_processing.translate(t1, src=lang_src, dest="en")

            epic_no = text_processing.get_epic_number(t2)
            data = text_processing.process_electoral_data(en_t.text)

            if data == None:
                continue

            data['epic_number'] = epic_no
            data['state'] = state
            res = db_client['dump_data'].find_one(
                {"epic_number": data['epic_number'], "s_id_1": data['s_id_1']})
            data['ac'] = ac
            data['pc'] = pc
            data['part_number'] = part_no
            data['part_name'] = part_name
            data['links'] = []

            if not res:
                bulk_data.append(data)

        db_client['dump_data'].insert_many(bulk_data)

    except Exception as e:
        raise e
    finally:
        driver.close()


def handle_voter_info_scrape(db_client, req):
    driver = get_driver()
    try:
        voter_info.get_info(db_client, driver, req)
    except Exception as e:
        raise e
    finally:
        driver.close()
