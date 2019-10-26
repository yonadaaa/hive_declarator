from django.shortcuts import render
import requests
import plotly.graph_objs as go
import plotly.offline as opy


def index(request):
    types_of_ranking = ["cars", "incomes", "properties"]
    context = {'types_of_ranking': types_of_ranking}
    return render(request, 'polls/index.html', context)


def get_declarations(year):
    declarations = []

    # api-endpoint
    url = "https://declarator.org/api/v1/search/sections"
    max_pages = 2
    i = 0
    while url and i < max_pages:
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
    for declaration in declarations:
        personal_info = declaration['main']['person']
        person_id = personal_info['id']
        person_name = personal_info['name']
        if person_id not in counts:
            counts[person_id] = {'name': person_name, 'count': 0}
        counts[person_id]['count'] = counting_function(declaration)
    return counts


def count_incomes(declaration):
    return int(sum(income["size"] for income in declaration["incomes"]))  # convert to int because who cares about kopeks


def count_vehicles(declaration):
    return len(declaration["vehicles"])


def count_properties(declaration):
    return len(declaration["real_estates"])


def graph_div(counts, layout_title_text):
    fig = go.Figure(
        data=[go.Bar(x=[value["name"] for value in counts],
                     y=[value["count"] for value in counts])],
        layout_title_text=layout_title_text
    )
    div = opy.plot(fig, auto_open=False, output_type='div')
    return div


def rankings_context(counts, title):
    sorted_counts = sorted(counts.values(), key=lambda v: v['count'], reverse=True)

    div = graph_div(sorted_counts[:10], title)

    return {'rankings': sorted_counts, 'graph': div}


def cars(request):
    year = 2018
    counts = count(year, count_vehicles)

    return render(request, 'polls/display_rankings.html', rankings_context(counts, "Top 10 officials for vehicle ownership"))


def incomes(request):
    year = 2018
    counts = count(year, count_incomes)

    return render(request, 'polls/display_rankings.html', rankings_context(counts, "Top 10 officials for income"))


def properties(request):
    year = 2018
    counts = count(year, count_properties)

    return render(request, 'polls/display_rankings.html', rankings_context(counts, "Top 10 officials for property ownership"))
