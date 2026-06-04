#!/usr/bin/env python3
"""
Servidor local do Validador de Anilhas CTO — InternetWay
Roda em http://localhost:8765
Também funciona como proxy para o buscacontratos.php (resolve CORS)
"""

import http.server
import urllib.request
import urllib.parse
import json
import os

import os
PORT = int(os.environ.get('PORT', 8765))
SINAIS_URL = 'http://intraweb.internetway.com.br/ctos/buscacontratos.php'

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Silencia logs desnecessários
        if '/proxy' in (args[0] if args else ''):
            print(f'  → Proxy: {args[1]} {args[0].split()[1] if args else ""}')

    def do_GET(self):
        # Serve o index.html e arquivos estáticos
        if self.path == '/' or self.path == '/index.html':
            self.servir_arquivo('index.html', 'text/html; charset=utf-8')
        else:
            self.send_error(404, 'Não encontrado')

    def do_POST(self):
        # Proxy para o buscacontratos.php
        if self.path == '/proxy/buscar':
            self.proxy_buscar()
        elif self.path == '/proxy/debug':
            self.proxy_debug()
        else:
            self.send_error(404, 'Não encontrado')

    def do_OPTIONS(self):
        # Responde preflight CORS
        self.send_response(200)
        self.headers_cors()
        self.end_headers()

    def headers_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def servir_arquivo(self, nome, tipo):
        caminho = os.path.join(os.path.dirname(__file__), nome)
        try:
            with open(caminho, 'rb') as f:
                conteudo = f.read()
            self.send_response(200)
            self.send_header('Content-Type', tipo)
            self.send_header('Content-Length', len(conteudo))
            self.headers_cors()
            self.end_headers()
            self.wfile.write(conteudo)
        except FileNotFoundError:
            self.send_error(404, f'{nome} não encontrado')

    def proxy_buscar(self):
        try:
            # Lê o body da requisição
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            anilhas = data.get('anilhas', [])

            if not anilhas:
                self.responder_json({'erro': 'Nenhuma anilha enviada'}, 400)
                return

            # Monta o POST para o buscacontratos.php
            payload = urllib.parse.urlencode({'anilhas': '\n'.join(anilhas)}).encode('utf-8')
            req = urllib.request.Request(
                SINAIS_URL,
                data=payload,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 ValidadorCTO/1.0'
                }
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                # Tenta UTF-8 primeiro, depois latin-1
                try:
                    html = raw.decode('utf-8')
                except UnicodeDecodeError:
                    html = raw.decode('latin-1', errors='replace')
                # Normaliza "NÂº" → "Nº" (latin-1 mal interpretado como UTF-8)
                html = html.replace('NÂº', 'Nº').replace('NÃ', 'N').replace('Â°', '°')

            # Parseia a tabela do HTML retornado
            linhas = parsear_tabela_html(html)

            self.responder_json({
                'ok': True,
                'total': len(linhas),
                'dados': '\n'.join(linhas)  # formato TSV igual ao texto copiado
            })

        except urllib.error.URLError as e:
            print(f'  ✗ Erro ao conectar no sinais.php: {e}')
            self.responder_json({
                'erro': 'Não foi possível conectar ao sinais.php. Verifique se está na rede interna.',
                'detalhe': str(e)
            }, 503)
        except Exception as e:
            print(f'  ✗ Erro: {e}')
            self.responder_json({'erro': str(e)}, 500)

    def proxy_debug(self):
        """Retorna o HTML bruto do sinais.php para depuração"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
            anilhas = data.get('anilhas', [])
            payload = urllib.parse.urlencode({'anilhas': '\n'.join(anilhas)}).encode('utf-8')
            req = urllib.request.Request(
                SINAIS_URL, data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded',
                         'User-Agent': 'Mozilla/5.0 ValidadorCTO/1.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                # Tenta UTF-8 primeiro, depois latin-1
                try:
                    html = raw.decode('utf-8')
                except UnicodeDecodeError:
                    html = raw.decode('latin-1', errors='replace')
                # Normaliza "NÂº" → "Nº" (latin-1 mal interpretado como UTF-8)
                html = html.replace('NÂº', 'Nº').replace('NÃ', 'N').replace('Â°', '°')
            linhas = parsear_tabela_html(html)
            self.responder_json({'html_preview': html[:3000], 'linhas_tsv': linhas})
        except Exception as e:
            self.responder_json({'erro': str(e)}, 500)

    def responder_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.headers_cors()
        self.end_headers()
        self.wfile.write(body)


def parsear_tabela_html(html):
    """Extrai linhas da tabela HTML e retorna lista de strings TSV"""
    import re
    linhas = []

    # Acha todas as linhas <tr>
    trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    for tr in trs:
        # Extrai células <td>
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL | re.IGNORECASE)
        if len(tds) < 3:
            continue
        # Remove tags HTML e limpa espaços
        cols = []
        for td in tds:
            texto = re.sub(r'<[^>]+>', '', td)
            texto = texto.replace('&nbsp;', ' ').replace('&amp;', '&')
            texto = texto.replace('&lt;', '<').replace('&gt;', '>')
            texto = ' '.join(texto.split())
            cols.append(texto)

        # Ignora cabeçalho
        if cols[0].lower() == 'contrato':
            continue

        # Só processa linhas com número de contrato válido
        num = ''.join(c for c in cols[0] if c.isdigit())
        if len(num) < 4:
            continue

        linhas.append('\t'.join(cols))

    return linhas


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print('=' * 55)
    print('  VALIDADOR DE ANILHAS CTO — InternetWay')
    print('=' * 55)
    print(f'  Servidor: http://localhost:{PORT}')
    print(f'  Proxy:    http://localhost:{PORT}/proxy/buscar')
    print('  Abrindo navegador...')
    print('  Para encerrar: feche esta janela ou Ctrl+C')
    print('=' * 55)

    # No Railway não abre navegador
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Servidor encerrado.')
