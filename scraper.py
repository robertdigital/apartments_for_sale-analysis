import os
from bs4 import BeautifulSoup
import csv
import json
import uuid
import requests


URL = "https://www.otodom.pl/sprzedaz/mieszkanie/lublin/?search%5Bregion_" \
      "id%5D=3&search%5Bsubregion_id%5D=396&search%5Bcity_id%5D=190"


class HousingOffers:
    def __init__(self, **kwargs):
        self.meters = kwargs.pop("meters", None)
        self.price = kwargs.pop("price", None)

    def __str__(self):
        return "{meters} {price}".format(**self.__dict__)


def fix(offer):
    replacements = {
        "m²": "",
        "zł": "",
        "pln": "",
        " ": "",
        ",": ".",
    }

    for k, v in replacements.items():
        offer.meters = offer.meters.replace(k, v)
        offer.price = offer.price.replace(k, v)

    offer.meters = offer.meters.strip()
    offer.price = offer.price.strip()


def extract_next_url(text):
    soup = BeautifulSoup(text, 'lxml')
    tag = soup.find(attrs={"data-dir": "next"})
    return tag.attrs["href"] if tag else None


def extract_offers(text):
    offers = []
    soup = BeautifulSoup(text, 'lxml')
    for offer in soup.find_all(class_='offer-item-details'):
        meters = offer.find(class_='hidden-xs offer-item-area').text
        price = offer.find(class_='offer-item-price').text.strip()
        offer = HousingOffers(meters=meters,
                              price=price)
    fix(offer)
    offers.append(offer)
    return offers


def main():
    session = requests.Session()
    session.headers["USER-AGENT"] = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64;"
        "Trident/7.0; rv:11.0) like Gecko"
    )

    next_url = URL
    dir_id = str(uuid.uuid4())
    output_dir = os.path.join("data", dir_id)
    os.makedirs(output_dir, exist_ok=True)

    page_id = 0

    while next_url:
        page_id += 1
        response = session.get(next_url)

        if response.ok:
            print("Extract")
            source = response.text
            offers = extract_offers(source)

            output_filename = os.path.join(output_dir,
                                           "plik-%d.json" % page_id)

            with open(output_filename, 'w', encoding='utf-8') as json_file:
                json.dump([o.__dict__ for o in offers], json_file)
                print("WROTE:", output_filename)

        else:
            print("ERROR")

        next_url = extract_next_url(source)
        print(next_url)

    # create_result_file()

        #
        # csvwriter = csv.DictWriter(csvfile,
        #                            fieldnames=["meters", "price"],
        #                            delimiter=',')
        # csvwriter.writeheader()
        # csvwriter.writerows([o.__dict__ for o in offers])

if __name__ == "__main__":
    main()
