from django.http import HttpResponse
from django.shortcuts import render
import requests


def index(request):
    latest_question_list = ["cars", "incomes"]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def get_declarations(year):
    declarations = []

    # api-endpoint
    URL = "https://declarator.org/api/v1/search/sections"
    i = 0
    while URL and i<2:
        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'year': year}

        # sending get request and saving the response as response object
        r = requests.get(url=URL, params=PARAMS)

        # extracting data in json format
        data = r.json()
        declarations += data["results"]

        URL = data["next"]
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


def count_incomes(decl):
    hi = decl["incomes"]
    return sum(income["size"] for income in hi)


def count_vehicles(decl):
    return len(decl["vehicles"])


def cars(request):
    field = "vehicles"
    year = 2018
    counts = count(year, count_vehicles)
    response = " "
    zesty = sorted(counts.items(), key=lambda kv: kv[1]['count'], reverse=True)
    for i in range(len(zesty)):
        response += "<p>{}: {} declared {} cars in {} </p>".format(i+1, zesty[i][1]['name'], zesty[i][1]['count'], year)

    return HttpResponse(response)


def incomes(request):
    field = "incomes"
    year = 2018
    counts = count(year, count_incomes)
    response = "<strong> Largest incomes for year {} in rub.</strong>".format(year)
    zesty = sorted(counts.items(), key=lambda kv: kv[1]['count'], reverse=True)
    for i in range(len(zesty)):
        response += "<p>{}: {} with {}₽</p>".format(i+1, zesty[i][1]['name'], int(zesty[i][1]['count']))

    return HttpResponse(response)


# TODO is it Rubles?
# wait I'm and idiot you can search for declarations not personal info


# decleration is made of family_name, given_name, id, name, patronymic_name, sections

# sections may be broken up into different objects depending on positions served?
