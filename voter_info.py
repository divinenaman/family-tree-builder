from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

import os
from datetime import datetime
import time
import text_processing

import captcha_solver


def save_scrape_request(db, data):

    if len(data) > 0:
        for i in range(len(data)):
            data[i]['scraped'] = False
            data[i]['type'] = 'scraper'

        db['scrape_req'].insert_many(data)


def get_info(db, driver, data):
    # data = {
    #     "name": "d",
    #     "father": "d",
    #     "age": "18",
    #     "gender": "male",
    #     "state": "Uttar Pradesh",
    #     "ac": "didarganj"
    # }

    driver.get('https://electoralsearch.in/')

    popup = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'continue')))
    popup.click()

    if "name" in data:
        driver.find_element(By.ID, 'name1').send_keys(data["name"])

    if "father" in data:
        driver.find_element(By.ID, 'txtFName').send_keys(data["father"])

    if "age" in data:
        select_age = Select(driver.find_element(By.ID, 'ageList'))
        select_age.select_by_visible_text(data["age"])

    if "gender" in data:
        select_g = Select(driver.find_element(By.ID, 'listGender'))
        select_g.select_by_value(data["gender"][0].upper())

    if 'state' in data:
        select_state = Select(driver.find_element(By.ID, 'nameStateList'))
        select_state.select_by_visible_text(data["state"].title())
    
    time.sleep(2)

    if 'district' in data:
        select_d = Select(driver.find_element(
            By.XPATH, "//select[@ng-model='selectedDistrict']"))
        
        mn = float('inf')
        val = ""
        for o in select_d.options:
            score = text_processing.compare_text(data['district'], o.text)
            
            
            if mn > score:
                mn = score
                val = o.get_attribute("value")
        
        select_d.select_by_value(val)

    time.sleep(2)

    if 'ac' in data:
        select_ac = Select(driver.find_element(
            By.XPATH, "//select[@ng-model='selectedAC']"))

        mn = float('inf')
        val = ""
        for o in select_ac.options:
            score = text_processing.compare_text(data['ac'], o.text)
            
            
            if mn > score:
                mn = score
                val = o.get_attribute("value")
        
        select_ac.select_by_value(val)

    retry = 0
    max_retry = 3
    
    while retry < max_retry:

        captacha_img = driver.find_element(By.ID, "captchaDetailImg")

        img_path = os.path.join("tmp", f'{datetime.now().timestamp()}_img.png')
        captacha_img.screenshot(img_path)

        ans = captcha_solver.manual(img_path)

        print(ans)

        c_in = driver.find_element(By.ID, 'txtCaptcha')
        c_in.send_keys(ans)

        b = driver.find_element(By.ID, 'btnDetailsSubmit')
        driver.execute_script("arguments[0].click();", b)

        # WebDriverWait(driver, 30).until(
        #     EC.presence_of_element_located((By.ID, 'resultsTable')))

        time.sleep(3)

        forms = driver.find_elements(
            By.XPATH, "//form[@action='/Home/VoterInformation']")

        if len(forms) == 0:
            retry += 1
        else:
            retry = max_retry + 1

        original_window = driver.current_window_handle

        data = []

        for f in forms:
            f.click()

            tabs = driver.window_handles
            for t in tabs:
                if (t != original_window):
                    driver.switch_to.window(t)

            WebDriverWait(driver, 90).until(EC.presence_of_element_located(
                (By.XPATH, f"//input[@id='state']/following-sibling::td")))

            st = driver.find_element(
                By.XPATH, f"//input[@id='state']/following-sibling::td")
            pc = driver.find_element(
                By.XPATH, f"//input[@id='parliment']/following-sibling::td")
            ac = driver.find_element(
                By.XPATH, f"//input[@id='ac_name']/following-sibling::td")
            n = driver.find_element(
                By.XPATH, f"//input[@id='name']/following-sibling::td")

            e = driver.find_element(
                By.XPATH, f"//input[@id='epic_no']/following-sibling::td")

            pno = driver.find_element(
                By.XPATH, f"//input[@id='part_no']/following-sibling::td")
            pn = driver.find_element(
                By.XPATH, f"//input[@id='part_name']/following-sibling::td")

            data.append({
                "state": st.text,
                "pc": pc.text,
                "ac": ac.text,
                "name": n.text,
                "epic": e.text,
                "part_no": pno.text,
                "part_name": pn.text
            })

            driver.close()
            driver.switch_to.window(original_window)

        save_scrape_request(db, data)
