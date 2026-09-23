import ipaddress
import re
from urllib.parse import urlparse, urlunparse

SUFIXOS = (".com.br", ".net.br", ".org.br", ".com", ".net", ".org", ".br")

PRIVADOS = re.compile(r"^(localhost|.*\.local|.*\.internal)$", re.IGNORECASE)


class UrlInvalida(ValueError):
    pass


def _host(url):
    host = (urlparse(url).hostname or "").lower()
    return host.removeprefix("www.")


def validar(url):
    partes = urlparse((url or "").strip())

    if partes.scheme not in ("http", "https"):
        raise UrlInvalida("a URL precisa começar com http:// ou https://")

    host = (partes.hostname or "").lower()
    if not host:
        raise UrlInvalida("endereço sem domínio válido")

    if PRIVADOS.match(host):
        raise UrlInvalida("endereços locais não são permitidos")

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None:
        raise UrlInvalida("informe o endereço do site, não um IP")

    if "." not in host:
        raise UrlInvalida("endereço sem domínio válido")

    return partes


def normalizar(url):
    partes = validar(url)
    host = (partes.hostname or "").lower().removeprefix("www.")
    caminho = partes.path.rstrip("/") or "/"
    return urlunparse(("https", host, caminho, "", "", ""))


def detectar_loja(url):
    host = _host(url)
    for sufixo in SUFIXOS:
        if host.endswith(sufixo):
            host = host[: -len(sufixo)]
            break
    return host.split(".")[-1] if host else "desconhecida"