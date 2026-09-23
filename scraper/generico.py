"""Extrator de preço independente de loja."""

import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
}


class ErroDeColeta(Exception):
    """Base para falhas ao coletar um preço."""


class PrecoNaoEncontrado(ErroDeColeta):
    """A página foi lida, mas nenhuma estratégia encontrou preço."""


class AcessoBloqueado(ErroDeColeta):
    """O site devolveu uma página de verificação em vez do conteúdo."""


def _para_numero(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = re.sub(r"[^\d,.]", "", str(valor))
    if not texto:
        return None

    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return None


def _achar_produto(no):
    if isinstance(no, list):
        for item in no:
            achado = _achar_produto(item)
            if achado:
                return achado
    elif isinstance(no, dict):
        tipo = no.get("@type", "")
        if "Product" in (tipo if isinstance(tipo, str) else " ".join(tipo)):
            return no
        if "@graph" in no:
            return _achar_produto(no["@graph"])
    return None


def _via_jsonld(soup):
    for bloco in soup.find_all("script", type="application/ld+json"):
        try:
            produto = _achar_produto(json.loads(bloco.string or "{}"))
        except json.JSONDecodeError:
            continue
        if not produto:
            continue

        ofertas = produto.get("offers")
        if isinstance(ofertas, list):
            ofertas = ofertas[0] if ofertas else {}
        ofertas = ofertas or {}

        preco = _para_numero(ofertas.get("price") or ofertas.get("lowPrice"))
        if preco:
            return produto.get("name"), preco
    return None


def _via_opengraph(soup):
    for prop in ("product:price:amount", "og:price:amount"):
        tag = soup.find("meta", property=prop)
        if tag and tag.get("content"):
            preco = _para_numero(tag["content"])
            if preco:
                titulo = soup.find("meta", property="og:title")
                return (titulo.get("content") if titulo else None), preco
    return None


def _via_microdata(soup):
    tag = soup.find(attrs={"itemprop": "price"})
    if tag:
        preco = _para_numero(tag.get("content") or tag.get_text(strip=True))
        if preco:
            nome = soup.find(attrs={"itemprop": "name"})
            return (nome.get_text(strip=True) if nome else None), preco
    return None


ESTRATEGIAS = (
    ("json-ld", _via_jsonld),
    ("open-graph", _via_opengraph),
    ("microdata", _via_microdata),
)


def extrair(html):
    soup = BeautifulSoup(html, "html.parser")

    for nome_estrategia, estrategia in ESTRATEGIAS:
        resultado = estrategia(soup)
        if resultado:
            nome, preco = resultado
            if not nome:
                titulo = soup.find("title")
                nome = titulo.get_text(strip=True) if titulo else "(sem nome)"
            return {"nome": nome.strip(), "preco": preco, "estrategia": nome_estrategia}

    raise PrecoNaoEncontrado("nenhuma estratégia encontrou preço nesta página")


def scrape(url):
    resposta = requests.get(url, headers=HEADERS, timeout=25)
    resposta.raise_for_status()

    html = resposta.text

    try:
        dados = extrair(html)
    except PrecoNaoEncontrado:
        if _parece_bloqueio(html):
            raise AcessoBloqueado(
                "o site respondeu com uma página de verificação automática"
            ) from None
        raise

    dados["coletado_em"] = datetime.now()
    return dados


MARCAS_BLOQUEIO = (
    "captcha",
    "automated access",
    "suspicious-traffic",
    "unusual traffic",
    "enter the characters",
    "digite os caracteres",
    "access denied",
)


def _parece_bloqueio(html):
    baixo = html.lower()
    if any(marca in baixo for marca in MARCAS_BLOQUEIO):
        return True
    return len(html) < 10_000 and "<title" not in baixo