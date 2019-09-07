from bs4 import BeautifulSoup
import csv
import requests


URL = "https://www.otodom.pl/sprzedaz/mieszkanie/lublin/?search%5Bregion_id%5D=3&search%5Bsubregion" \
      "_id%5D=396&search%5Bcity_id%5D=190"


class HousingOffers:
    def __init__(self, **kwargs):
        self.meters = kwargs.pop("meters", None)
        self.price = kwargs.pop("price", None)

    def __str__(self):
        return "{meters} {price}".format(**self.__dict__)


def extract(text):
    offers = []
    soup = BeautifulSoup(text, 'lxml')
    for offer in soup.find_all(class_='offer-item-details'):
        meters = offer.find(class_='hidden-xs offer-item-area').text
        price = offer.find(class_='offer-item-price').text.strip()
        offers.append(HousingOffers(meters=meters,
                                    price=price))
    with open('data/plik.csv', 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(offers)

    return offers

extract(URL)

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
