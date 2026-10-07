import os
import sys
import requests
from dotenv import load_dotenv
import litellm

# 1. Carregar variáveis do ficheiro .env
load_dotenv()

BASE_URL = os.getenv("ATLASSIAN_BASE_URL", "").rstrip("/")
EMAIL = os.getenv("ATLASSIAN_USER_EMAIL", "")
TOKEN = os.getenv("ATLASSIAN_API_TOKEN", "")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

auth = (EMAIL, TOKEN)
headers = {"Accept": "application/json"}

print("=" * 60)
print("TESTE DE CONECTIVIDADE DAS APIS (SDLC AI QA AGENT)")
print("=" * 60)

status_ok = True

# --- 2. Teste Jira Cloud REST API ---
print("\n[1/3] A validar Jira Cloud REST API...")
if not BASE_URL or not EMAIL or not TOKEN:
    print("  ❌ ERRO: Faltam variáveis da Atlassian no .env.")
    status_ok = False
else:
    try:
        url_jira = f"{BASE_URL}/rest/api/3/myself"
        res_jira = requests.get(url_jira, auth=auth, headers=headers, timeout=10)
        if res_jira.status_code == 200:
            user_data = res_jira.json()
            print(f"  ✅ Jira Conectado! Utilizador: {user_data.get('displayName')} ({user_data.get('emailAddress')})")
            
            if PROJECT_KEY:
                res_proj = requests.get(f"{BASE_URL}/rest/api/3/project/{PROJECT_KEY}", auth=auth, headers=headers, timeout=10)
                if res_proj.status_code == 200:
                    print(f"  ✅ Projeto Jira '{PROJECT_KEY}' confirmado!")
                else:
                    print(f"  ⚠️ Aviso: Projeto '{PROJECT_KEY}' não encontrado ou sem permissão (HTTP {res_proj.status_code}).")
        else:
            print(f"  ❌ Falha no Jira: HTTP {res_jira.status_code} - {res_jira.text[:100]}")
            status_ok = False
    except Exception as e:
        print(f"  ❌ Exceção na chamada ao Jira: {e}")
        status_ok = False

# --- 3. Teste Confluence Cloud REST API ---
print("\n[2/3] A validar Confluence Cloud REST API...")
if BASE_URL and EMAIL and TOKEN:
    try:
        url_conf = f"{BASE_URL}/wiki/rest/api/space"
        res_conf = requests.get(url_conf, auth=auth, headers=headers, timeout=10)
        if res_conf.status_code == 200:
            spaces = res_conf.json().get("results", [])
            print(f"  ✅ Confluence Conectado! Espaços disponíveis: {len(spaces)}")
        else:
            print(f"  ❌ Falha no Confluence: HTTP {res_conf.status_code} - {res_conf.text[:100]}")
            status_ok = False
    except Exception as e:
        print(f"  ❌ Exceção na chamada ao Confluence: {e}")
        status_ok = False

# --- 4. Teste Anthropic Claude via LiteLLM ---
print("\n[3/3] A validar Anthropic Claude API...")
if not ANTHROPIC_KEY:
    print("  ❌ ERRO: ANTHROPIC_API_KEY não definida no .env.")
    status_ok = False
else:
    # 4.1 Descobrir modelos disponíveis na tua conta
    anthropic_headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01"
    }
    modelo_a_usar = None
    try:
        res_models = requests.get("https://api.anthropic.com/v1/models", headers=anthropic_headers, timeout=10)
        if res_models.status_code == 200:
            modelos_disponiveis = [m["id"] for m in res_models.json().get("data", [])]
            print(f"  ℹ️ Modelos disponíveis na tua conta: {modelos_disponiveis}")
            
            # Prioridade de escolha: Sonnet > Haiku > Qualquer Claude disponível
            for preferido in ["claude-3-5-sonnet", "claude-3-7-sonnet", "claude-3-5-haiku", "claude-3-haiku"]:
                for m in modelos_disponiveis:
                    if preferido in m:
                        modelo_a_usar = f"anthropic/{m}"
                        break
                if modelo_a_usar:
                    break
            
            if not modelo_a_usar and modelos_disponiveis:
                modelo_a_usar = f"anthropic/{modelos_disponiveis[0]}"
        else:
            # Fallback seguro caso o endpoint de modelos não responda
            modelo_a_usar = "anthropic/claude-3-haiku-20240307"
    except Exception:
        modelo_a_usar = "anthropic/claude-3-haiku-20240307"

    if not modelo_a_usar:
        modelo_a_usar = "anthropic/claude-3-haiku-20240307"

    print(f"  🔄 A testar inferência com: {modelo_a_usar}...")
    try:
        os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_KEY
        response = litellm.completion(
            model=modelo_a_usar,
            messages=[{"role": "user", "content": "Responde apenas com a palavra: OK"}],
            max_tokens=10
        )
        reply = response.choices[0].message.content.strip()
        print(f"  ✅ Claude Conectado via '{modelo_a_usar}'! Resposta: '{reply}'")
    except Exception as e:
        print(f"  ❌ Falha na API da Anthropic: {e}")
        status_ok = False

print("\n" + "=" * 60)
if status_ok:
    print("TODAS AS LIGAÇÕES FORAM VALIDADAS COM SUCESSO! 🚀")
    sys.exit(0)
else:
    print("EXISTEM FALHAS NA CONFIGURAÇÃO. Revê o ficheiro .env. ⚠️")
    sys.exit(1)