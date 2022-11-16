from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import os
from datetime import datetime
import text_processing
import time
import captcha_solver


def get_uttar_pradesh_by_data(driver, req):
    driver.get("http://ceouttarpradesh.nic.in/rollpdf/rollpdf.aspx")

    ac = text_processing.rm_spaces(req['ac'].split('-')[0])
    part_number = int(text_processing.rm_spaces(req['part_no']))
    pc = text_processing.rm_spaces(req['pc'])

    """
    Select district & AC
    
    """

    # district_idx_threshold = 2
    # district_idx = 1
    # found = False
    # while district_idx < district_idx_threshold:

    # district
    select_district = Select(driver.find_element(
        By.ID, 'ctl00_ContentPlaceHolder1_DDLDistrict'))
    select_district.select_by_visible_text(pc)

    # ac
    select_ac = Select(driver.find_element(
        By.ID, 'ctl00_ContentPlaceHolder1_DDL_AC'))
    select_ac.select_by_visible_text(ac)

    show_btn = driver.find_element(
        By.ID, 'ctl00_ContentPlaceHolder1_Button1')
    show_btn.click()

    page_number = (part_number // 20) + (1 if part_number % 20 > 0 else 0)
    max_page_number = 10
    current_page = 1

    while page_number > max_page_number:
        last_page_btn = driver.find_element(
            By.XPATH, f"//a[@href=\"javascript:__doPostBack('ctl00$ContentPlaceHolder1$ElecRollGrd','Page${max_page_number + 1}')\"]")
        last_page_btn.click()
        current_page = max_page_number + 1
        max_page_number += 10

    if current_page != page_number:
        required_page_btn = driver.find_element(
            By.XPATH, f"//a[@href=\"javascript:__doPostBack('ctl00$ContentPlaceHolder1$ElecRollGrd','Page${page_number}')\"]")
        required_page_btn.click()

    pdf_link = driver.find_element(
        By.XPATH, f"//td[contains(text(),{part_number})]/following-sibling::td/a[contains(text(),'View')]")
    pdf_link.click()

    main_window = driver.current_window_handle
    tabs = driver.window_handles
    for t in tabs:
        if (t != main_window):
            driver.switch_to.window(t)

    captacha_img = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_Image1')))

    img_path = os.path.join("tmp", f'{datetime.now().timestamp()}_img.png')
    captacha_img.screenshot(img_path)

    ans = captcha_solver.manual(img_path)

    captcha_input = driver.find_element(
        By.ID, 'ctl00_ContentPlaceHolder1_txtimgcode')
    captcha_input.send_keys(ans)

    verify_captcha = driver.find_element(
        By.ID, 'ctl00_ContentPlaceHolder1_Button1')
    verify_captcha.click()

    # download_pdf = WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located((By.ID, 'download')))
    # download_pdf.click()

    time.sleep(10)


def get_tamil_nadu_by_data(driver, req):
    driver.get("https://www.elections.tn.gov.in/rollpdf/SSR2022_MR_05012022.aspx")

    ac = text_processing.rm_spaces(req['ac'].split('-')[0])
    part_number = int(text_processing.rm_spaces(req['part_no']))
    pc = text_processing.rm_spaces(req['pc'])

    ac_ta = text_processing.translate(
        text=ac, src="en", dest="ta").text.replace(" ", "")
    pc_ta = text_processing.translate(
        text=pc, src="en", dest="ta").text.replace(" ", "")

    """
    Select district & AC
    
    """

    # district_idx_threshold = 2
    # district_idx = 1
    # found = False
    # while district_idx < district_idx_threshold:

    # district
    select_district = Select(driver.find_element(
        By.ID, 'ddl_District'))

    mn = float('inf')
    val = ""
    for o in select_district.options:
        score = text_processing.compare_text(pc_ta, o.text)
        print(o.text, pc)
        if mn > score:
            mn = score
            val = o.get_attribute("value")
    select_district.select_by_value(val)

    time.sleep(3)

    # ac
    select_ac = Select(driver.find_element(
        By.ID, 'ddl_Assembly'))

    mn = float('inf')
    val = ""
    for o in select_ac.options:
        score = text_processing.compare_text(ac_ta, o.text)

        if mn > score:
            mn = score
            val = o.get_attribute("value")
    select_ac.select_by_value(val)

    show_btn = driver.find_element(
        By.ID, 'btn_Login')
    show_btn.click()

    page_number = (part_number // 20) + (1 if part_number % 20 > 0 else 0)
    max_page_number = 10
    current_page = 1

    # while page_number > max_page_number:
    #     last_page_btn = driver.find_element(
    #         By.XPATH, f"//a[@href=\"javascript:__doPostBack('ctl00$ContentPlaceHolder1$ElecRollGrd','Page${max_page_number + 1}')\"]")
    #     last_page_btn.click()
    #     current_page = max_page_number + 1
    #     max_page_number += 10

    # if current_page != page_number:
    #     required_page_btn = driver.find_element(
    #         By.XPATH, f"//a[@href=\"javascript:__doPostBack('ctl00$ContentPlaceHolder1$ElecRollGrd','Page${page_number}')\"]")
    #     required_page_btn.click()

    pdf_link = driver.find_element(
        By.XPATH, f"//input[starts-with(@name,'lvCustomers')][@value='{part_number}']/following-sibling::td//a[starts-with(@href,'https://www.elections.tn.gov.in/rollpdf')]")
    pdf_link.click()

    # main_window = driver.current_window_handle
    # tabs = driver.window_handles
    # for t in tabs:
    #     if (t != main_window):
    #         driver.switch_to.window(t)

    captacha_img = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'capCode')))

    img_path = os.path.join("tmp", f'{datetime.now().timestamp()}_img.png')
    captacha_img.screenshot(img_path)

    ans = captcha_solver.manual(img_path)

    captcha_input = driver.find_element(
        By.ID, 'txt_Vcode')
    captcha_input.send_keys(ans)

    verify_captcha = driver.find_element(
        By.ID, 'btn_Login')
    verify_captcha.click()

    iframe = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//iframe[starts-with(@src,'https://www.elections.tn.gov.in')]")))
    driver.switch_to.frame(iframe)

    download_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//a[starts-with(@href,'https://www.elections.tn.gov.in')]")))
    download_btn.click()

    time.sleep(5)
