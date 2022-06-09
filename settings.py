import json
import re
from typing import List, Any
import requests
from bs4 import BeautifulSoup


# function for extract kfc address
def get_or_none(obj, *keys: list[str]) -> Any:
    for attr in keys:
        if obj.get(attr) is not None:
            obj = obj.get(attr)
        else:
            return
    return obj


class Parser:
    @staticmethod
    def monomah_parse(url: str) -> list[Any]:
        data = []
        res = requests.get(url)
        stores = re.findall(r'Placemark\([\w\W]+?\}', res.text)

        for store in stores:
            address = re.search(r'\w+[А-ЯЁа-яё].*\s*\w+[А-ЯЁа-яё]\,*\s*\w+\S', store).group(0)
            latlon = re.search(r'\d{2}\.\d{6,20}\,\s+\d{2}\.\d{6,20}', store).group(0).split(',')
            phone = re.search(r'\+\d{3}\s*\(*\d{2}\)*\s*\d{3}\s*\d{2}\s*\d{2}', store).group(0)

            data.append({
                "address": address,
                "latlon": [float(latlon[0]),
                           float(latlon[1])],
                "name": "Мономах",
                "phones": f"{phone}"
            })
        return data

    @staticmethod
    def kfc_parse(url: str) -> list[Any]:
        data = []

        res = requests.get(url)
        api_data = res.text

        restaurants = json.loads(api_data)

        for restaurant in restaurants['searchResults']:
            st = restaurant.get("storePublic")
            address = get_or_none(st, "contacts", "streetAddress", "ru")
            if address is not None:
                address = " ".join(address.split()[1:])

            latlon = restaurant['storePublic']['contacts']['coordinates']['geometry']['coordinates']
            name = restaurant['storePublic']['title']['ru']
            phones = restaurant['storePublic']['contacts']['phoneNumber']
            start_end = restaurant['storePublic']['openingHours']['regular']

            working_hours = ["closed"] if restaurant['storePublic']['status'] == "Closed" \
                else (
                [f"пн-пт {start_end['startTimeLocal']} до {start_end['endTimeLocal']},"
                 f" сб-вс {start_end['startTimeLocal']}-{start_end['endTimeLocal']}"]
            )

            data.append({
                "address": address,
                "latlon": latlon,
                "name": name,
                "phones": [phones],
                "working_hours": working_hours
            })

        return data

    @staticmethod
    def ziko_parse(url: str) -> list[Any]:
        data = []
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            points = soup.find_all('tr', class_='mp-pharmacy-element')

            for point in points:
                link = point.find('div', class_='morepharmacy').find('a', href=True)
                req = requests.get("https://www.ziko.pl" + link['href'])
                soup = BeautifulSoup(req.text, 'lxml')

                span_list = soup.find_all('span', attrs={'style': "margin-left: 5px;"})

                name = span_list[0].text
                address = f"{span_list[1].text}, {span_list[2].text}"
                phone = span_list[4].text
                hours = point.find('td', class_='mp-table-hours').find_all('span')

                coords = soup.find('div', class_='coordinates').find_all('span')
                lat = ''.join(i for i in coords[0].text if not i.isalpha())
                lon = ''.join(i for i in coords[1].text if not i.isalpha())
                latlon = [float(lat[3:]), float(lon[3:])]

                data.append({
                    "address": address,
                    "latlon": latlon,
                    "name": name,
                    "phones": [phone],
                    "working_hours": [i.text for i in hours]
                })

            return data

        except requests.exceptions.RequestException:
            raise requests.exceptions.RequestException(f"Error {url}")
