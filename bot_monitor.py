import logging
import threading
import time
from bs4 import cloudscraper  # ou cloudscraper puro
import cloudscraper
from flask import Flask
import requests

# Configuração de logs
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = "9188416522:AAGlTfA0DOyNb4iBOawykAC1W5p51jYJ1hs"
CHAT_ID = "5170284090"
URL_ALVO = "https://baozinho.com/atualizacoes"

ultimo_estado_conhecido = None

# Cria um mini servidor web para o Render não desligar o bot
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot de Monitoramento do Baozinho está Rodando 24/7!"


def enviar_alerta_telegram(mensagem: str):
    url_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    dados = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url_api, data=dados, timeout=10)
    except Exception as e:
        logging.error(f"Erro ao enviar Telegram: {e}")


def loop_monitoramento():
    """Função que roda o monitoramento em segundo plano num loop infinito."""
    global ultimo_estado_conhecido
    logging.info("Loop de monitoramento em segundo plano iniciado...")

    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )

    # Envia aviso de que ligou
    enviar_alerta_telegram(
        "🤖 Bot monitor do Baozinho foi iniciado com sucesso na nuvem!"
    )

    while True:
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

                if ultimo_estado_conhecido is None:
                    ultimo_estado_conhecido = estado_atual
                    logging.info("Estado inicial guardado com sucesso!")
                elif estado_atual != ultimo_estado_conhecido:
                    mensagem = f"🚨 **NOVAS ATUALIZAÇÕES DETETADAS!** 🚨\n\nNovidades:\n{estado_atual}"
                    enviar_alerta_telegram(mensagem)
                    ultimo_estado_conhecido = estado_atual
                    logging.info("Atualização detetada e enviada!")
                else:
                    logging.info("Nenhuma alteração no site.")
            else:
                logging.warning(
                    f"Site retornou status code: {resposta.status_code}"
                )

        except Exception as e:
            logging.error(f"Erro no loop de monitoramento: {e}")

        # Aguarda 20 minutos antes da próxima verificação
        time.sleep(1200)


def iniciar_thread_monitoramento():
    """Inicia o monitoramento numa linha paralela para não trancar o servidor web."""
    t = threading.Thread(target=loop_monitoramento)
    t.daemon = True
    t.start()


if __name__ == "__main__":
    # Inicia o monitoramento em paralelo
    iniciar_thread_monitoramento()
    # Sobe o servidor web do Flask (necessário para o Render)
    app.run(host="0.0.0.0", port=10000)
