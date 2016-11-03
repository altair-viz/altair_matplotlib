import os

import pandas as pd
import altair

from altair_matplotlib.utils import chart_data

CSV_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data.csv'))
JSON_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data.json'))


def _make_data():
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
