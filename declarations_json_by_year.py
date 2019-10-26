import json
import requests


def get_declarations(year):
    declarations = []

    # api-endpoint
    url = "https://declarator.org/api/v1/search/sections"
    max_pages = 403
    page_number = 0
    while url and page_number < max_pages:
        print(page_number)
        # defining a params dict for the parameters to be sent to the API
        params = {'year': year}

        # sending get request and saving the response as response object
        r = requests.get(url=url, params=params)

        # extracting data in json format
        data = r.json()
        declarations += data["results"]

        url = data["next"]
        page_number += 1

    return declarations


def main():
    year = 2018
    declarations_2018 = get_declarations(year)

    with open('declarations_2018.json', 'w') as outfile:
        json.dump(declarations_2018, outfile)


if __name__ == '__main__':
    main()
