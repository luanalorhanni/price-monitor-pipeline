from scraper import generico

# Exceções por loja, quando o genérico não der conta.
# Vazio de propósito: hoje nenhuma loja precisa de tratamento especial.
ESPECIFICOS = {}


def coletar(url, loja=None):
    scraper = ESPECIFICOS.get(loja, generico.scrape)
    return scraper(url)