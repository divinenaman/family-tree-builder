import db
import text_processing
import image_processing
import pdf
import electoral_pdf
import voter_info

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import os
import time

from dotenv import load_dotenv
load_dotenv()


db_client = db.get_client()['family-tree']




voter_info.get_info(driver)






# images = pdf.pdf_as_image_crops("tmp/PopupCaptcha.pdf")

# file1 = open('text_dump_hi', 'w')
# file2 = open('text_dump.txt', 'w')
# file3 = open('text_dump_err.txt', 'w')

# for m1, m2 in images:
#     try:
#         # info
#         t1 = image_processing.image_to_text(m1, lang="Devanagari")
#         t1 = list(map(lambda x: text_processing.rm_special_characters(x), t1.split('\n')))
#         t1 = list(map(lambda x: text_processing.rm_spaces(x), t1))
#         t1 = '\n'.join(t1)

#         # epic number
#         t2 = image_processing.image_to_text(m2)

#         en_t = text_processing.translate(t1, src="hi", dest="en")

#         file1.write(t1)
#         file1.write('\n')
#         file1.write(t2)
#         file1.write('\n')
#         file1.write('\n')

#         file2.write(en_t.text)
#         file2.write('\n')
#         file2.write(t2)
#         file2.write('\n')
#         file2.write('\n')

#         epic_no = text_processing.get_epic_number(t2)
#         data = text_processing.process_electoral_data(en_t.text)

#         if data == None:
#             continue

#         data['epic_number'] = epic_no

#         db_client['dump_data'].insert_one(data)

#     except Exception as e:
#         file3.write(str(e))
#         file3.write('\n')
#         file3.write('\n')

#         print(str(e))

# file2.close()
# file1.close()
# file3.close()
