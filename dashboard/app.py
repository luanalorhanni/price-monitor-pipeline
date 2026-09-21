import dash
import dash_bootstrap_components as dbc
from dash import html

from dashboard.data import buscar_resumo

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Price Monitor"


def card_produto(produto):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(produto["name"], className="card-title"),
                html.H4(f"R$ {produto['current_price']}", className="text-primary"),
                html.Small(f"mínima histórica: R$ {produto['min_price_ever']}"),
                html.Br(),
                html.Small(f"{produto['pct_above_min']}% acima da mínima"),
                html.Br(),
                dbc.Badge(produto["store"], color="secondary", className="mt-2"),
            ]
        ),
        className="mb-3 h-100",
    )


def servir_layout():
    produtos = buscar_resumo()
    return dbc.Container(
        [
            html.H2("Price Monitor", className="my-4"),
            dbc.Row([dbc.Col(card_produto(p), md=4) for p in produtos]),
        ],
        fluid=True,
    )


app.layout = servir_layout


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)