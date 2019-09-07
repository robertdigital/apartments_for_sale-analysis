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
        self.id = kwargs.pop("id", None)
        self.meters = kwargs.pop("meters", None)
        self.price = kwargs.pop("price", None)

    def __str__(self):
        return "{id} {meters} {price}".format(**self.__dict__)


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
    next_url = tag.attrs["href"] if tag else None
    return next_url


def extract_offers(text):
    offers = []
    soup = BeautifulSoup(text, 'lxml')
    articles = soup.find_all(class_="offer_item")
    for offer in articles:
        id = offer.attrs['data-item-id'].text.strip()
        details = offer.find(class_='offer-item-details')
        meters = details.find(class_='hidden-xs offer-item-area').text
        price = details.find(class_='offer-item-price').strip()

        offer = HousingOffers(id=id,
                              meters=meters,
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
            next_url = extract_next_url(source)

            output_filename = os.path.join(output_dir,
                                           "plik-%d.json" % page_id)

            with open(output_filename, 'w', encoding='utf-8') as json_file:
                json.dump([o.__dict__ for o in offers], json_file)
                print("WROTE:", output_filename)

        else:
            print("ERROR")

        #next_url = extract_next_url(source)
        print(next_url)

    create_result_file(output_dir)


def create_result_file(directory):
    merge_dict = {}
    for entry in os.listdir(directory):
        if entry.endswith(".json"):
            json_file = os.path.join(directory, entry)
            offers = json.load(open(json_file, "r"))
            for o in offers:
                merge_dict[o["id"]] = o
    print(merge_dict)


    output_filename = os.path.join(directory, "results.csv")
    with open(output_filename, 'w+', encoding='utf-8') as csvfile:
        csvwriter = csv.DictWriter(csvfile,
                               fieldnames=["id", "meters", "price"],
                               delimiter=',')
        csvwriter.writeheader()
        csvwriter.writerows(merge_dict.values())



if __name__ == "__main__":
    main()
