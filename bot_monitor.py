import logging
from bs4 import BeautifulSoup
import cloudscraper
import requests

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "9188416522:AAGlTfA0DOyNb4iBOawykAC1W5p51jYJ1hs"
CHAT_ID = "5170284090"
URL_ALVO = "https://baozinho.com/atualizacoes"


def enviar_alerta_telegram(mensagem: str):
    url_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    dados = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url_api, data=dados, timeout=10)
    except Exception as e:
        logging.error(f"Erro ao enviar Telegram: {e}")


def verificar_novas_atualizacoes():
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )

    try:
        logging.info(f"A verificar atualizações em: {URL_ALVO}")
        resposta = scraper.get(URL_ALVO, timeout=20)

        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.text, "html.parser")
            links = soup.find_all("a")
            primeiros_links = []
            for link in links:
                texto = link.get_text().strip()
                if (
                    texto
                    and len(primeiros_links) < 5
                    and not texto.startswith("http")
                ):
                    primeiros_links.append(texto)

            estado_atual = (
                " | ".join(primeiros_links[:3])
                if primeiros_links
                else "Sem dados"
            )

            # Como o GitHub Actions desliga e liga de novo a cada 20 min,
            # para guardar o estado anterior de uma execução para outra,
            # o ideal é enviar a notificação se houver mudança ou salvar num arquivo de cache.
            # Para testes rápidos, ele vai rodar e checar o topo do site.
            
            mensagem = f"🔍 **Verificação realizada no GitHub Actions**\nTopo atual:\n{estado_atual}"
            enviar_alerta_telegram(mensagem)
            
        else:
            logging.warning(f"Site retornou status code: {resposta.status_code}")

    except Exception as e:
        logging.error(f"Erro no monitoramento: {e}")


if __name__ == "__main__":
    verificar_novas_atualizacoes()
