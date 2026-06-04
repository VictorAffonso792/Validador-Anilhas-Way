# 🔌 Validador de Anilhas CTO — InternetWay

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-orange?logo=html5&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Railway-purple?logo=railway&logoColor=white)
![License](https://img.shields.io/badge/Licença-MIT-green)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen)

Sistema web interno para validação de anilhas (portas de fibra óptica) em CTOs (Caixas de Terminação Óptica). Desenvolvido para auxiliar agentes de suporte durante atendimentos de campo com técnicos da InternetWay.

---

## 📸 Preview

> _Adicione um screenshot do sistema aqui: `docs/preview.png`_

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📋 **Inserção flexível** | Aceita anilhas em qualquer formato: lista, vírgula, espaço ou uma por linha |
| 🔍 **Consulta automática** | Busca no sistema sinais.php via proxy — sem copiar e colar |
| 🔄 **Re-consulta inteligente** | Se anilhas não forem encontradas, tenta automaticamente com `00` na frente |
| 🟢 **Status dos contratos** | Identifica: Normal, Cancelado, Encerrado, Bloqueio Financeiro |
| 🟣 **Detecção de legados** | Detecta contratos migrados (L-hemp) e exibe número antigo → número novo |
| 🏠 **Validação de endereço** | Compara número da casa informado pelo técnico com o cadastro |
| 📊 **Relatório copiável** | Gera relatório formatado para colar diretamente no atendimento |
| 📡 **Tipo de CTO** | Indica automaticamente CTO padrão (8 portas) ou ampliada (16 portas) |

### 🎨 Chips visuais — 4 estados de cor

```
🟢 Verde    → encontrada + compatível (contrato ativo, encontrado direto)
🔴 Vermelho → encontrada + todos cancelados
🟣 Roxo     → encontrada via zeros (ex: 61936 → 0061936) ou via legado (ex: 15306 → 0060222)
⚫ Cinza    → não encontrada em nenhuma tentativa
```

---

## 🛠️ Tecnologias

- **Frontend:** HTML5 + CSS3 + JavaScript puro (vanilla, sem frameworks, sem npm)
- **Backend:** Python 3.11 — apenas biblioteca padrão, sem dependências externas
- **Deploy:** [Railway](https://railway.app)
- **Proxy:** Servidor HTTP interno que resolve o bloqueio de CORS com o sistema legado

---

## 🏗️ Arquitetura

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   Usuário   │────▶│   index.html     │────▶│   server.py             │
│  (browser)  │◀────│   (frontend)     │◀────│   /proxy/buscar         │
└─────────────┘     └──────────────────┘     └────────────┬────────────┘
                                                           │
                                                           ▼
                                              ┌─────────────────────────┐
                                              │  buscacontratos.php     │
                                              │  (rede interna ISP)     │
                                              └─────────────────────────┘
```

### Por que o proxy é necessário?

O sistema `sinais.php` roda na intranet da InternetWay (`intraweb.internetway.com.br`) sem cabeçalhos CORS. Isso impede que o navegador faça requisições diretas a partir de outro domínio. O `server.py` resolve isso agindo como intermediário — o frontend chama `/proxy/buscar` no mesmo servidor, e o servidor Python faz a requisição para a intranet.

### Lógica de busca em 3 tentativas

O técnico em campo pode informar o número da anilha de formas diferentes do que está cadastrado no sistema. Para cobrir todos os casos:

```
1. DIRETO    → "118747" bate com "118747" no sistema ✅
2. ZEROS     → "61936"  bate com "0061936" (normaliza zeros de ambos) ✅
3. LEGADO    → "15306"  bate com "15306" no código L-hemp do contrato "0060222" ✅
               (formato: "Contrato Nº 60222 (L-hemp00313-15306)")
```

### Re-consulta automática com "00"

```
1ª consulta: 11 anilhas enviadas → 8 retornadas → 3 não encontradas
             Sistema detecta faltantes automaticamente
2ª consulta: "00" + anilhas faltantes → ex: "15306" vira "0015306"
             Resultados das duas consultas são mesclados
```

---

## 📋 Pré-requisitos

- **Python 3.11+** instalado
- Acesso à **rede interna da InternetWay** (para o proxy funcionar)
- Conta no **Railway** (para deploy em produção)

---

## 💻 Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/validador-anilhas-cto.git
cd validador-anilhas-cto

# 2. Rode o servidor
python server.py

# 3. Acesse no navegador
# http://localhost:8765
```

**No Windows:** clique duas vezes no arquivo `iniciar.bat` — o servidor inicia e o navegador abre automaticamente.

> ⚠️ O proxy só funciona quando o computador tem acesso à rede interna da InternetWay (escritório ou VPN).

---

## 🚀 Deploy no Railway

### Passo a passo

**1.** Faça login em [railway.app](https://railway.app) com sua conta GitHub

**2.** Clique em **New Project** → **Deploy from GitHub repo**

**3.** Selecione o repositório `validador-anilhas-cto`

**4.** O Railway detecta o `Procfile` automaticamente e inicia o build

**5.** Aguarde ~2 minutos — a URL é gerada automaticamente no formato:
```
https://validador-anilhas-cto.railway.app
```

**6.** Compartilhe a URL com os colegas — nenhuma instalação necessária!

> ⚠️ **Importante:** O Railway precisa ter acesso à rede interna da InternetWay para o proxy funcionar. Verifique se o servidor do Railway consegue alcançar `intraweb.internetway.com.br`.

### Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `PORT` | Porta do servidor | `8765` (definida automaticamente pelo Railway) |

---

## 📁 Estrutura do projeto

```
validador-anilhas-cto/
├── index.html          # Frontend completo (HTML + CSS + JS)
├── server.py           # Servidor Python + proxy para sinais.php
├── Procfile            # Instrução de deploy para o Railway
├── requirements.txt    # Dependências Python (nenhuma externa)
├── runtime.txt         # Versão do Python (3.11.0)
└── README.md           # Esta documentação
```

---

## 📖 Guia do usuário

### Fluxo completo

```
PASSO 1 — Inserir Anilhas
  Cole os números enviados pelo técnico (um por linha, vírgula ou espaço)
  Clique em "Consultar no sinais.php"

PASSO 2 — Consulta Automática
  O sistema busca automaticamente no sinais.php
  Se anilhas não forem encontradas, re-consulta com "00" automaticamente
  Acompanhe os chips: cinza = aguardando, colorido = encontrado

PASSO 3 — Resultado Processado
  Chips coloridos mostram o status de cada anilha
  Tabela separada: Compatíveis | Todos Cancelados
  Contratos legados mostram: número técnico → número sistema
  Clique em "Copiar Relatório" para gerar texto para o atendimento

PASSO 4 — Validar Endereço com Técnico
  Para cada anilha compatível, pergunte ao técnico o número da casa
  Digite o número no campo correspondente
  Sistema compara automaticamente:
    ✓ CONFERE  → número bate com o cadastro
    ✗ DIVERGE  → número diferente (Cadastro: 20 | Técnico: 22)
    ⚠ SEM NÚM → endereço sem número identificável
  Use "Validar Todos" para processar em lote
```

### Entendendo os chips de anilhas

Após o processamento, cada anilha enviada pelo técnico aparece como um chip colorido:

| Cor | Significado |
|---|---|
| 🟢 **Verde** | Encontrada e compatível (pelo menos 1 contrato ativo) |
| 🔴 **Vermelho** | Encontrada mas todos os contratos estão cancelados |
| 🟣 **Roxo** | Encontrada via zeros (`61936 → 0061936`) ou via legado (`15306 → 0060222`) |
| ⚫ **Cinza** | Não retornada pelo sistema em nenhuma tentativa |

### Entendendo a tabela de resultados

- **Coluna Anilha:** quando encontrada via legado, mostra o número do técnico e o número do sistema:
  ```
  15306        ← número que o técnico conhece
  → 0060222    ← número cadastrado no sistema
  ```
- **Coluna Contratos:** tag `LEGADO` em roxo indica contrato migrado de outro provedor
- **Coluna Nº Casa:** número extraído automaticamente do endereço cadastrado

---

## ⚙️ Observações técnicas

- O sistema só funciona com acesso à rede interna da InternetWay
- O `sinais.php` retorna HTML com encoding misto (latin-1/UTF-8), normalizado pelo servidor
- Contratos legados têm formato: `Contrato NÂº XXXXX (L-hemp00313-YYYYY)`
- O número do contrato antigo está no código L-hemp após o último hífen: `L-hemp00313-`**`15306`**
- Um contrato só é considerado "legado diferente" quando o número dentro do L-hemp é diferente do número da anilha atual — evita falsos positivos

---

## 📄 Licença

MIT License — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">
  Desenvolvido para uso interno — InternetWay 🌐
</div>
