import altair as alt


def theme_1(*args, **kwargs):
    return {
        "width": 400,
        "height": 300,
        "config": {
            "line": {"strokeWidth": 4,},
            "style": {"bar": {"size": 20}},
            "legend": {"symbolSize": 100, "titleFontSize": 20, "labelFontSize": 20},
            "axis": {"titleFontSize": 20, "labelFontSize": 20},
        },
    }


alt.themes.register("theme_1", theme_1)


from tabulate import tabulate


def format_label(nome):
    return " ".join(nome.split("_")).title()


def riepilogo_campo(nome, today, yesterday):
    if nome in ("incremento", "percentuale_positivi", "percentuale_nuovi_positivi"):
        return (
            f"{format_label(nome)}",
            f"{today.loc[nome]:.02f}%",
            f"{today.loc[nome] - yesterday.loc[nome]:+.02f}",
        )

    return (
        f"{format_label(nome)}",
        today.loc[nome],
        f"{today.loc[nome] - yesterday.loc[nome]:+.00f}",
    )


def tabella_riassuntiva(today, yesterday):
    rows = [
        riepilogo_campo(nome, today, yesterday)
        for nome in (
            "totale_casi",
            "totale_positivi",
            "tamponi",
            "casi_testati",
            "deceduti",
            "dimessi_guariti",
            "terapia_intensiva",
            "incremento",
            "percentuale_positivi",
            "percentuale_nuovi_positivi",
        )
    ]
    return tabulate(rows, headers=["", "Oggi", "Variazione"], tablefmt="html")


def grafici_riassuntivi(df):
    base = alt.Chart(df).mark_line().encode(
        x='data:T',
        tooltip=['data', 'nuovi_positivi', 'incremento', 'nuovi_deceduti'],
    ).properties(
        width=600,
        height=200
    ).interactive()

    return alt.vconcat(
        base.encode(y='nuovi_positivi'),
        base.encode(y=alt.Y(f'incremento:Q', scale=alt.Scale(domain=(0, 20)))),
        base.encode(y='nuovi_deceduti'),
        base.encode(y='terapia_intensiva'),
        base.encode(y='nuovi_tamponi'),
        base.encode(y='variazione_totale_positivi'),
        base.encode(y='percentuale_positivi'),
        base.encode(y=alt.Y(f'percentuale_nuovi_positivi:Q', scale=alt.Scale(domain=(0, 20)))),
        base.encode(y='letalita'),
    )