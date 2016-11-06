"""Utilities for Altair-matplotlib"""

from collections import defaultdict

import pandas as pd
import altair

# Thoughs on how to do this...
#
# 1) extract the dataframe from the chart
# 2) If there are any encodings with aggregations:
#        group by all non-aggregates and aggregate
# 3) Extract necessary columns and rename by encoding
# 4) Create mapping of feature to plot element
# 4) Group-by everything but
#    - x, y, x2, y2
#    - size (if continuous)
#    - color (if continuous)
#


def chart_data(chart, parent=None):
    """Get chart data as dataframe"""
    if isinstance(chart.data, pd.DataFrame):
        return chart.data
    elif isinstance(chart.data, altair.Data):
        if chart.data.url:
            if chart.data.url.endswith('csv'):
                return pd.read_csv(chart.data.url)
            else:
                return pd.read_json(chart.data.url)
        else:
            return pd.DataFrame(chart.data.values)
    elif chart.data is None and parent is not None:
        return DataGrouper(parent)._extract_data()
    else:
        raise ValueError("Chart has no recognizable data")


def group_by_encoding(chart):
    """Do Group-by operations implied by encodings.

    Parameters
    ----------
    chart : Chart object
        Should have data and encoding defined

    Returns
    -------
    grouped : DataFrame
        The grouped results
    """
    chart._finalize()

    data = chart_data(chart)
    encoding = chart.encoding

    defined_encodings = {t: getattr(encoding, t)
                         for t in encoding.trait_names()
                         if getattr(encoding, t) is not None}

    # TODO: handle timeUnit groupings as well
    if any(encoding.timeUnit is not None for encoding in defined_encodings.values()):
        raise NotImplementedError("timeUnit")

    # TODO: handle transformed & filtered data
    if chart.transform is not None:
        raise NotImplementedError("transformed/filtered data")

    # Extract group and aggregate names
    group_fields = []
    group_names = []
    aggregates = defaultdict(dict)
    for name, encoding in defined_encodings.items():
        if encoding.field is not None:
            if encoding.aggregate is None:
                group_fields.append(encoding.field)
                group_names.append(name)
            else:
                aggregates[encoding.field][name] = encoding.aggregate

    # Group and aggregate
    grouped = data.groupby(group_fields).aggregate(aggregates)
    grouped.index.names = group_names
    grouped.columns = grouped.columns.droplevel()
    grouped = grouped.reindex_axis(sorted(grouped.columns), axis=1)
    grouped = grouped.reset_index()

    return grouped
