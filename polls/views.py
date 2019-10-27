from django.shortcuts import render
import requests
import plotly.graph_objs as go
import plotly.offline as opy
import json


def count_with_family_name(year, counting_function):
    declarations = get_declarations_from_file()

    counts = {}
    for declaration in declarations:
        personal_info = declaration['main']['person']
        person_id = personal_info['id']
        person_name = personal_info['family_name']
        if person_id not in counts:
            counts[person_id] = {'name': person_name, 'count': 0}
        counts[person_id]['count'] = counting_function(declaration)
    return counts


def index(request):
    types_of_ranking = ["cars", "incomes", "properties", "land"]

    year = 2018
    counts = count_with_family_name(year, count_vehicles)
    bleh = rankings_context(counts, "Top 10 officials for vehicle ownership", "%{y:.0f} vehicles")

    context = {'types_of_ranking': types_of_ranking, 'graph': bleh["graph"]}
    return render(request, 'polls/index.html', context)


def get_declarations_from_api(year):
    declarations = []

    # api-endpoint
    url = "https://declarator.org/api/v1/search/sections"
    max_pages = 2
    page_number = 0
    while url and page_number < max_pages:
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


def get_declarations_from_file():
    filename = 'declarations_2018.json'
    with open(filename) as json_file:
        declarations = json.load(json_file)
    return declarations


def count(year, counting_function):
    declarations = get_declarations_from_file()

    counts = {}
    for declaration in declarations:
        personal_info = declaration['main']['person']
        person_id = personal_info['id']
        person_name = personal_info['name']
        if person_id not in counts:
            counts[person_id] = {'name': person_name, 'count': 0}
        counts[person_id]['count'] = counting_function(declaration)
    return counts


def count_incomes(declaration):
    return int(sum(income["size"] for income in declaration["incomes"]))


def count_vehicles(declaration):
    return len(declaration["vehicles"])


def count_properties(declaration):
    return len(declaration["real_estates"])

def count_land(declaration):
    return int(sum(real_estate["square"] for real_estate in declaration["real_estates"] if real_estate["square"]))


def graph_div(counts, layout_title_text, hover_template):
    fig = go.Figure(
        data=[go.Bar(x=[value["name"] for value in counts],
                     y=[value["count"] for value in counts],
                     hovertemplate=hover_template,
                     )],
        layout_title_text=layout_title_text,
    )
    div = opy.plot(fig, auto_open=False, output_type='div')
    return div


def rankings_context(counts, title, hover_template):
    sorted_counts = sorted(counts.values(), key=lambda v: v['count'], reverse=True)

    for i in range(len(sorted_counts)):
        sorted_counts[i]["rank"] = i+1

    div = graph_div(sorted_counts[:20], title, hover_template)

    return {'rankings': sorted_counts, 'graph': div}


def cars(request):
    year = 2018
    counts = count(year, count_vehicles)

    context = rankings_context(counts, "Top 20 officials for vehicle ownership", "%{y:.0f} vehicles")
    return render(request, 'polls/display_rankings.html', context)


def incomes(request):
    year = 2018
    counts = count(year, count_incomes)

    context = rankings_context(counts, "Top 20 officials for income", "₽%{y:.0f}")
    return render(request, 'polls/display_rankings.html', context)


def properties(request):
    year = 2018
    counts = count(year, count_properties)

    context = rankings_context(counts, "Top 20 officials for property ownership", "%{y:.0f} properties")
    return render(request, 'polls/display_rankings.html', context)


def land_owned(request):
    year = 2018
    counts = count(year, count_land)

    context = rankings_context(counts, "Top 20 officials for land ownership", "%{y:.0f} square metres")
    return render(request, 'polls/display_rankings.html', context)
