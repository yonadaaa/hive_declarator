from django.shortcuts import render
import requests
import plotly.graph_objs as go
import plotly.offline as opy
import json


def rankings_context_homepage(counts, title, hover_template):
    sorted_counts = sorted(counts.values(), key=lambda v: v['count'], reverse=True)

    div = graph_div_homepage(sorted_counts[:10], title, hover_template)

    return {'graph': div}


def graph_div_homepage(counts, layout_title_text, hover_template):
    fig = go.Figure(
        data=[go.Bar(x=[value["name"] for value in counts],
                     y=[value["count"] for value in counts],
                     hovertemplate=hover_template,
                     )],
        layout_title_text=layout_title_text,
    )
    fig.update_layout(
        margin=go.layout.Margin(l=8, r=8, b=8, t=35, pad=0)
    )
    div = opy.plot(fig, auto_open=False, output_type='div')
    return div


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
    types_of_ranking = ["vehicles", "incomes", "properties", "land"]
    counting_functions = [count_vehicles, count_incomes, count_properties, count_land]
    graph_titles = ["Top 10 for most vehicles owned", "Top 10 for income", "Top 10 for property ownership" ,"Top 10 for most land owned"]

    year = 2018
    hello = []
    for i in range(len(types_of_ranking)):
        counts = count_with_family_name(year, counting_functions[i])
        bleh = rankings_context_homepage(counts, graph_titles[i], "%{y:.0f}")
        hello.append({"graph": bleh["graph"], "name": types_of_ranking[i]})

    context = {'hello': hello}
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


def count_by_party(declarations, year, counting_function):

    counts = {}
    for declaration in declarations:
        party_info = declaration['main']['party']
        if party_info:
            if party_info["id"] not in counts:
                counts[party_info["id"]] = {'name': party_info["name"], 'count': 0}
            counts[party_info["id"]]['count'] = counting_function(declaration)
            counts[party_info["id"]]['count'] = counting_function(declaration)
    return counts


def count(declarations, year, counting_function):

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
    sum = 0
    for real_estate in declaration["real_estates"]:
        if real_estate["square"]:
            if real_estate["share"]:
                sum += real_estate["share"]*real_estate["square"]
            else:
                sum += real_estate["square"]
    return int(sum)


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


def rankings_context(counts, party_counts, title, party_title, hover_template):
    sorted_counts = sorted(counts.values(), key=lambda v: v['count'], reverse=True)
    sorted_party_counts = sorted(party_counts.values(), key=lambda v: v['count'], reverse=True)

    for i in range(len(sorted_counts)):
        sorted_counts[i]["rank"] = i+1

    div = graph_div(sorted_counts[:20], title, hover_template)
    party_div = graph_div(sorted_party_counts, party_title, hover_template)

    return {'rankings': sorted_counts, 'graph': div, "party_graph": party_div}


def vehicles(request):
    year = 2018
    declarations = get_declarations_from_file()
    counts = count(declarations, year, count_vehicles)
    party_counts = count_by_party(declarations, year, count_vehicles)

    context = rankings_context(counts,
                               party_counts,
                               "Top 20 officials for vehicle ownership",
                               "Vehicle ownership by party",
                               "%{y:.0f} vehicles")
    return render(request, 'polls/display_rankings.html', context)


def incomes(request):
    year = 2018
    declarations = get_declarations_from_file()

    counts = count(declarations, year, count_incomes)
    party_counts = count_by_party(declarations, year, count_incomes)

    context = rankings_context(counts,
                               party_counts,
                               "Top 20 officials for income",
                               "Total income by party",
                               "₽%{y:.0f}")
    return render(request, 'polls/display_rankings.html', context)


def properties(request):
    year = 2018
    declarations = get_declarations_from_file()
    counts = count(declarations, year, count_properties)
    party_counts = count_by_party(declarations, year, count_properties)

    context = rankings_context(counts,
                               party_counts,
                               "Top 20 officials for property ownership",
                               "Properties owned by party",
                               "%{y:.0f} properties")
    return render(request, 'polls/display_rankings.html', context)


def land_owned(request):
    year = 2018
    declarations = get_declarations_from_file()
    counts = count(declarations, year, count_land)
    party_counts = count_by_party(declarations, year, count_land)

    context = rankings_context(counts,
                               party_counts,
                               "Top 20 officials for land ownership",
                               "Land ownership by party",
                               "%{y:.0f} square metres")
    return render(request, 'polls/display_rankings.html', context)
