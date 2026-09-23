import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, callback, html

from dashboard.data import buscar_resumo, cadastrar_produto
from scraper.generico import PrecoNaoEncontrado, AcessoBloqueado
from scraper.lojas import UrlInvalida

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


def montar_cards():
    return [dbc.Col(card_produto(p), md=4) for p in buscar_resumo()]


def servir_layout():
    return dbc.Container(
        [
            html.H2("Price Monitor", className="my-4"),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="entrada-url",
                        placeholder="Cole aqui a URL do produto que quer monitorar",
                    ),
                    dbc.Button("Monitorar", id="botao-monitorar", color="primary"),
                ],
                className="mb-3",
            ),
            html.Div(id="aviso"),
            dbc.Row(montar_cards(), id="cards"),
        ],
        fluid=True,
    )


app.layout = servir_layout


@callback(
    Output("aviso", "children"),
    Output("cards", "children"),
    Input("botao-monitorar", "n_clicks"),
    State("entrada-url", "value"),
    prevent_initial_call=True,
)
def monitorar(n_clicks, url):
    try:
        mensagem = cadastrar_produto(url)
        aviso = dbc.Alert(mensagem, color="success", duration=6000)

    except UrlInvalida as erro:
        aviso = dbc.Alert(str(erro), color="warning")

    except AcessoBloqueado:
        aviso = dbc.Alert(
            "Este site bloqueia leitura automática e devolveu uma página de "
            "verificação em vez do produto. Não é possível monitorá-lo.",
            color="danger",
        )

    except PrecoNaoEncontrado:
        aviso = dbc.Alert(
            "Li a página, mas não encontrei o preço no HTML. O site pode "
            "carregar o preço por JavaScript.",
            color="danger",
        )

    except requests.HTTPError as erro:
        aviso = dbc.Alert(
            f"O site recusou a leitura automática (HTTP {erro.response.status_code}).",
            color="danger",
        )    

    return aviso, montar_cards()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)