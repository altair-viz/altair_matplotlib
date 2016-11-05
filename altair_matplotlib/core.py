import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import altair

from . import utils


def render(chart):
    """Render an Altair chart as a matplotlib figure

    Parameters
    ----------
    chart : altair.Chart
        a Chart, LayeredChart, or FacetedChart to render

    Returns
    -------
    fig : matplotlib.Figure
        the rendered Figure

    Raises
    ------
    NotImplementedError :
        Many portions of the Vega-Lite schema are not yet supported, and this
        routine raises a NotImplementedError when it encounters them.
    """
    # dispatch on chart type
    if isinstance(chart, altair.Chart):
        return _render_chart(chart)
    elif isinstance(chart, dict):
        return render(altair.Chart.from_dict(chart))
    elif isinstance(chart, string):
        return render(altair.Chart.from_json(chart))
    else:
        raise NotImplementedError("Chart type = {0}".format(type(chart)))


def _defined_traits(obj):
    if not obj:
        return []
    else:
        return [t for t in obj.trait_names() if getattr(obj, t)]


def _render_chart(chart):
    if chart.mark == 'line':
        return _render_line_chart(chart)
    else:
        raise NotImplementedError("mark = {0}".format(chart.mark))


def _render_line_chart(chart):
    data = utils.chart_data(chart)
    encodings = _defined_traits(chart.encoding)

    if chart.encoding.color:
        groups = data.groupby(chart.encoding.color.field)
        legend = True
    else:
        groups = [None, data]
        legend = False

    fig, ax = plt.subplots()

    for color, group in groups:
        ax.plot(group[chart.encoding.x.field],
                group[chart.encoding.y.field],
                label=str(color))

    if legend:
        ax.legend(title=chart.encoding.color.field)

    return fig
