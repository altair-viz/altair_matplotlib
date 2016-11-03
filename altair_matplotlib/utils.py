"""Utilities for Altair-matplotlib"""

import pandas as pd
import altair


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
        return chart_data(parent)
    else:
        raise ValueError("Chart has no recognizable data")
        
