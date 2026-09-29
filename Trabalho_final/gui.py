"""Interface web local do MovieLens Explorer, sem dependências externas."""

from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import threading
import time
import webbrowser

from search_service import MovieSearchService


INDEX = Path(__file__).with_name("index.html")


class EstadoAplicacao:
    def __init__(self):
        self.lock = threading.Lock()
        self.service = None
        self.carregando = False
        self.pronto = False
        self.erro = None
        self.mensagem = "Inicializando estruturas de dados..."
        self.progresso = 0
        self.stats = {}
        self.duracao = 0.0

    def iniciar_carga(self, modo):
        with self.lock:
            if self.carregando:
                return
            self.carregando, self.pronto, self.erro = True, False, None
            self.progresso, self.mensagem = 0, "Inicializando estruturas de dados..."

        def executar():
            inicio = time.perf_counter()
            try:
                service = MovieSearchService()

                def progresso(mensagem, percentual):
                    with self.lock:
                        self.mensagem, self.progresso = mensagem, percentual

                stats = service.carregar(modo, progresso)
                with self.lock:
                    self.service, self.stats = service, stats
                    self.duracao = time.perf_counter() - inicio
                    self.carregando, self.pronto = False, True
            except Exception as erro:
                with self.lock:
                    self.erro = str(erro)
                    self.carregando = False

        threading.Thread(target=executar, daemon=True).start()

    def status(self):
        with self.lock:
            return {
                "carregando": self.carregando,
                "pronto": self.pronto,
                "erro": self.erro,
                "mensagem": self.mensagem,
                "progresso": self.progresso,
                "stats": self.stats,
                "duracao": self.duracao,
            }


ESTADO = EstadoAplicacao()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        return

    def _json(self, dados, status=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _ler_json(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(tamanho) or b"{}")

    def do_GET(self):
        if self.path == "/":
            corpo = INDEX.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
        elif self.path == "/api/status":
            self._json(ESTADO.status())
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self._json({"erro": "Rota não encontrada."}, 404)

    def do_POST(self):
        try:
            dados = self._ler_json()
            if self.path == "/api/load":
                modo = dados.get("modo", "amostra")
                if modo not in ("amostra", "completo"):
                    raise ValueError("Modo de dados inválido.")
                ESTADO.iniciar_carga(modo)
                self._json({"mensagem": "Carregamento iniciado."}, 202)
            elif self.path == "/api/search":
                self._buscar(dados)
            else:
                self._json({"erro": "Rota não encontrada."}, 404)
        except (ValueError, json.JSONDecodeError) as erro:
            self._json({"erro": str(erro)}, 400)
        except Exception as erro:
            self._json({"erro": f"Erro interno: {erro}"}, 500)

    def _buscar(self, dados):
        service = ESTADO.service
        if not service or not ESTADO.pronto:
            self._json({"erro": "A base ainda está sendo carregada."}, 409)
            return
        tipo, campos = dados.get("tipo"), dados.get("campos", {})
        consultas = {
            "prefixo": lambda: service.buscar_prefixo(campos.get("prefixo", "")),
            "usuario": lambda: service.buscar_usuario(campos.get("usuario", "")),
            "genero": lambda: service.buscar_top_genero(
                campos.get("quantidade", ""), campos.get("genero", "")
            ),
            "tags": lambda: service.buscar_tags(
                campos.get("tag_1", ""), campos.get("tag_2", "")
            ),
            "periodo": lambda: service.buscar_melhores_periodo(
                campos.get("quantidade", ""),
                campos.get("ano_inicial", ""),
                campos.get("ano_final", ""),
            ),
        }
        if tipo not in consultas:
            raise ValueError("Tipo de consulta inválido.")
        self._json({"resultados": [asdict(item) for item in consultas[tipo]()]})


def executar(porta=8765, abrir_navegador=True):
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
    url = f"http://127.0.0.1:{servidor.server_port}"
    print(f"MovieLens Explorer disponível em {url}")
    print("Pressione Ctrl+C para encerrar.")
    if abrir_navegador:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nAplicação encerrada.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interface do MovieLens Explorer")
    parser.add_argument("--port", type=int, default=8765, help="Porta local do servidor")
    parser.add_argument("--no-browser", action="store_true", help="Não abrir o navegador automaticamente")
    args = parser.parse_args()
    executar(args.port, not args.no_browser)
