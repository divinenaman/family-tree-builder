import db
import scraper_handler
import time
import graph_linking
import random


def handle_pdf_scrape_req():
    print("------scraping electoral pdf---------")
    client = db.get_client()
    while True:
        check = client['scrape_req'].find(
            {"type": "scraper", "scraped": False})
        for c in check:
            try:
                print('scrape-pdf: start-scraping')
                scraper_handler.handle_electoral_pdf_scrape(client, c)
                print('scrape-pdf: end-scraping')
                client['scrape_req'].update_one(
                    {"_id": c['_id']}, {"$set": {"scraped": True}})
            except Exception as e:
                print('scrape-pdf: error-scraping')
                print("handle_pdf_scrape_req", str(e))
        time.sleep(5)


def handle_voter_scrape_req():
    print("------scraping voter info---------")
    client = db.get_client()
    while True:
        check = client['scrape_req'].find(
            {"type": "user", "scraped": False})
        for c in check:
            try:
                print('scrape-voter: start-scraping')
                scraper_handler.handle_voter_info_scrape(client, c)
                print('scrape-voter: start-scraping')
                client['scrape_req'].update_one(
                    {"_id": c['_id']}, {"$set": {"scraped": True}})
            except Exception as e:
                print('scrape-voter: error-scraping')
                print("handle_voter_scrape_req", str(e))

        time.sleep(5)


def handle_family_linking(threshold=500):
    print("------generating family links---------")
    sort_fields = ["age", "name"]
    client = db.get_client()
    while True:
        try:
            graph_linking.link_family(
                client, threshold=threshold, sort_field=random.choice(sort_fields))
        except Exception as e:
            print('family-link: error')
            print("handle_family_linking", e)

        time.sleep(5)
