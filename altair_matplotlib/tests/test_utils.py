import os

import pandas as pd
import altair

from altair_matplotlib.utils import chart_data, group_by_encoding

CSV_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data.csv'))
JSON_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data.json'))


def _make_data_files():
    data = pd.DataFrame({'x': [4, 5, 6],
                         'y': ['a', 'b', 'c'],
                         'z': [0.25, 0.5, 1.0]})
    data.to_csv(CSV_URL, orient='records', index=False)
    data.to_json(JSON_URL)


def test_chart_data():
    data = pd.read_csv(CSV_URL)

    # sanity check
    assert data.equals(pd.read_json(JSON_URL))

    chart1 = altair.Chart(data)
    chart2 = altair.Chart(CSV_URL)
    chart3 = altair.Chart(JSON_URL)

    # TODO: test layered charts

    data_by_value = altair.Data(values=data.to_dict(orient='records'))
    for datatype in [data, CSV_URL, JSON_URL, data_by_value]:
        chart = altair.Chart(datatype)
        assert data.equals(chart_data(chart))


def test_group_by_encoding():
    data = pd.DataFrame({'foo': [1, 1, 2, 2, 3, 3],
                         'bar': [1, 2, 3, 4, 5, 6],
                         'baz': ['a', 'b', 'c', 'd', 'e', 'f']})
    chart = altair.Chart(data).mark_point().encode(
        x='foo',
        y='mean(bar):Q',
        color=altair.Color(value='blue'),
        row=altair.Row(),
    )

    grouped = group_by_encoding(chart)
    expected = pd.DataFrame({'x': [1, 2, 3],
                             'y': [1.5, 3.5, 5.5]})

    assert grouped.equals(expected)


def test_group_by_multiple_aggregates():
    data = pd.DataFrame({'foo': [1, 1, 2, 2, 3, 3],
                         'bar': [1, 2, 3, 4, 5, 6],
                         'baz': ['a', 'b', 'c', 'd', 'e', 'f']})
    chart = altair.Chart(data).mark_point().encode(
        x='foo',
        y='min(bar):Q',
        y2='max(bar):Q'
    )

    grouped = group_by_encoding(chart)
    expected = pd.DataFrame({'x': [1, 2, 3],
                             'y': [1, 3, 5],
                             'y2': [2, 4, 6]})

    print(grouped)
    print(expected)

    assert grouped.equals(expected)
