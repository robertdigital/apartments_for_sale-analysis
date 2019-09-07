from bs4 import BeautifulSoup
import csv
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

def extract(text):
    offers = []
    soup = BeautifulSoup(text, 'lxml')
    for offer in soup.find_all(class_='offer-item-details'):
        meters = offer.find(class_='hidden-xs offer-item-area').text
        price = offer.find(class_='offer-item-price').text.strip()
        offers.append(HousingOffers(meters=meters,
                                    price=price))
    print(offers[0])
    # with open('data/plik.csv', 'w', encoding='utf-8') as csvfile:
    #     csvwriter = csv.DickWriter(csvfile, fieldnames=["meters", "price"])
    #     csvwriter.writerow(offers)

    return offers


def main():
    session = requests.Session()
    session.headers["USER-AGENT"] = (
        "Mozilla/5.0 (Windows NT 6.1; WOW64;"
        "Trident/7.0; rv:11.0) like Gecko"
    )

    response = session.get(URL)

    if response.ok:
        print("Extract")
        source = response.text
        extract(source)
    else:
        print("ERROR")


if __name__ == "__main__":
    main()
