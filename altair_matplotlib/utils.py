"""Utilities for Altair-matplotlib"""

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

    # Extract group names and associated fields
    group_names, group_fields = zip(*((name, encoding.field)
                                      for name, encoding in defined_encodings.items()
                                      if encoding.field is not None
                                      and encoding.aggregate is None))

    # Extract all aggregated encodings
    agg_names, agg_cols, aggs = zip(*((name, encoding.field, encoding.aggregate)
                                      for name, encoding in defined_encodings.items()
                                      if encoding.field is not None
                                      and encoding.aggregate is not None))

    # TODO: map VL aggregates to Pandas aggregates
    # This might raise an error for some...
    grouped = data.groupby(group_fields).aggregate(dict(zip(agg_cols, aggs)))
    grouped = grouped.reset_index()
    grouped = grouped.rename(columns=dict(zip(group_fields, group_names)))
    grouped = grouped.rename(columns=dict(zip(agg_cols, agg_names)))
    return grouped
