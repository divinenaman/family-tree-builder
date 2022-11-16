import sys
import cron_task

from dotenv import load_dotenv
load_dotenv()

s = sys.argv[1]

if s == "api":
    pass

elif s == "scrape-voter":
    cron_task.handle_voter_scrape_req()

elif s == "scrape-pdf":
    cron_task.handle_pdf_scrape_req()

elif s == "family-linker":
    cron_task.handle_family_linking(6000)

else:
    print('invalid args')