import altair as alt

def theme_1(*args, **kwargs):
    return {
        "width": 400,
        "height": 300,
        "config": {
            "line": {
               "strokeWidth": 4,
            },
            "style": {"bar": {"size": 20}},
            "legend": {"symbolSize": 100, "titleFontSize": 20, "labelFontSize": 20},
            "axis": {"titleFontSize": 20, "labelFontSize": 20},
        },
    }

alt.themes.register("theme_1", theme_1)