import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import altair


def render(chart):
    # dispatch on chart type
    if isinstance(chart, altair.Chart):
        return _render_chart(chart)
    elif isinstance(chart, altair.LayeredChart):
        return _render_layeredchart(chart)
    elif isinstance(chart, altair.FacetedChart):
        return _render_facetedchart(chart)
    elif isinstance(chart, dict):
        return render(altair.Chart.from_dict(chart))
    elif isinstance(chart, string):
        return render(altair.Chart.from_json(chart))


def _defined_traits(obj):
    if not obj:
        return []
    else:
        return [t for t in obj.trait_names() if getattr(obj, t)]


def _get_dataframe(chart):
    if isinstance(chart.data, pd.DataFrame):
        return chart.data
    else:
        raise NotImplementedError("data of type {0}".formattype(chart.data))


def _render_chart(chart):
    if chart.mark == 'line':
        return _render_line_chart(chart)
    else:
        raise NotImplementedError("mark = {0}".format(chart.mark))


def _render_line_chart(chart):
    data = _get_dataframe(chart)
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


def _render_layeredchart(chart):
    raise NotImplementedError("Faceted Chart")


def _render_facetedchart(chart):
    raise NotImplementedError("Layered Chart")
