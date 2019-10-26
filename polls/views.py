from django.http import HttpResponse
from django.shortcuts import render
import requests


def index(request):
    types_of_ranking = ["cars", "incomes"]
    context = {'types_of_ranking': types_of_ranking}
    return render(request, 'polls/index.html', context)


def get_declarations(year):
    declarations = []

    # api-endpoint
    url = "https://declarator.org/api/v1/search/sections"
    max_pages = 3
    i = 0
    while url and i<max_pages:
        # defining a params dict for the parameters to be sent to the API
        params = {'year': year}

        # sending get request and saving the response as response object
        r = requests.get(url=url, params=params)

        # extracting data in json format
        data = r.json()
        declarations += data["results"]

        url = data["next"]
        i += 1

    return declarations


def count(year, counting_function):
    declarations = get_declarations(year)

    counts = {}
    for decl in declarations:
        personal_info = decl['main']['person']
        person_id = personal_info['id']
        person_name = personal_info['name']
        if person_id not in counts:
            counts[person_id] = {'name': person_name, 'count': 0}
        counts[person_id]['count'] = counting_function(decl)
    return counts


def count_incomes(declaration):
    return sum(income["size"] for income in declaration["incomes"])


def count_vehicles(declaration):
    return len(declaration["vehicles"])


def cars(request):
    year = 2018
    counts = count(year, count_vehicles)
    zesty = sorted(counts.values(), key=lambda v: v['count'], reverse=True)

    context = {'rankings': zesty}
    return render(request, 'polls/display_rankings.html', context)


def incomes(request):
    year = 2018
    counts = count(year, count_incomes)
    zesty = sorted(counts.values(), key=lambda v: v['count'], reverse=True)

    context = {'rankings': zesty}
    return render(request, 'polls/display_rankings.html', context)
