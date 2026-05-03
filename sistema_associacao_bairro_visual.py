import os
import sqlite3
import re
import requests
from contextlib import closing
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

DB_NAME = "associacao.db"

st.set_page_config(
    page_title="Associação Ecopraça",
    page_icon="🏡",
    layout="wide"
)

def aplicar_estilo():
    st.markdown('''
    <style>
        /* PRODUTO SAAS PREMIUM - CSS CORE */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* 1. RESET E ESTRUTURA GLOBAL */
        :root {
            --primary: #10b981; /* Emerald 500 */
            --primary-dark: #059669;
            --zinc-50: #f8fafc;
            --zinc-100: #f1f5f9;
            --zinc-200: #e2e8f0;
            --zinc-500: #64748b;
            --zinc-800: #1e293b;
            --zinc-950: #0f172a;
        }

        .stApp {
            background-color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        /* Remove o padding padrão do Streamlit e a barra de decoração superior */
        [data-testid="stHeader"] { background: rgba(0,0,0,0); height: 0px; }
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px !important;
        }

        /* 2. TOP BAR PREMIUM */
        .top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0;
            border-bottom: 1px solid var(--zinc-100);
            margin-bottom: 2rem;
        }
        
        .brand-section { display: flex; align-items: center; gap: 12px; }
        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--zinc-950);
            letter-spacing: -0.02em;
        }
        .brand-subtitle {
            font-size: 0.875rem;
            color: var(--zinc-500);
            border-left: 1px solid var(--zinc-200);
            padding-left: 12px;
            margin-left: 4px;
        }

        /* 3. DASHBOARD CARDS (ESTILO VERCEL/LINEAR) */
        .metric-card {
            background: white;
            border: 1px solid var(--zinc-200);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .metric-card:hover {
            border-color: var(--zinc-800);
            box-shadow: 0 12px 20px -10px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }

        .metric-label {
            color: var(--zinc-500);
            font-size: 0.875rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .metric-value {
            color: var(--zinc-950);
            font-size: 2.25rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin-top: 8px;
        }

        /* Badge de Status */
        .badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 99px;
            background: var(--zinc-100);
            color: var(--zinc-500);
        }
        .badge-success { background: #dcfce7; color: #15803d; }

        /* 4. TABS NAVEGAÇÃO PRO */
        button[data-baseweb="tab"] {
            border: none !important;
            background: transparent !important;
            color: var(--zinc-500) !important;
            font-weight: 500 !important;
            padding: 8px 16px !important;
            transition: all 0.2s !important;
        }
        
        button[aria-selected="true"] {
            color: var(--zinc-950) !important;
            background: var(--zinc-100) !important;
            border-radius: 8px !important;
        }

        /* 5. FORMS E BOTÕES EXECUTIVOS */
        div[data-baseweb="input"] {
            border-radius: 8px !important;
            border: 1px solid var(--zinc-200) !important;
            transition: all 0.2s;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: var(--zinc-950) !important;
            box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1) !important;
        }

        div.stButton > button {
            background: var(--zinc-950) !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.25rem !important;
            border: 1px solid var(--zinc-950) !important;
            transition: all 0.15s;
        }
        
        div.stButton > button:hover {
            background: #27272a !important;
            transform: translateY(-1px);
        }

        /* Botão Secundário (Sair) */
        div[data-testid="stVerticalBlock"] > div:last-child div.stButton > button {
            background: white !important;
            color: var(--zinc-950) !important;
            border: 1px solid var(--zinc-200) !important;
        }

        /* 6. TABELAS (ESTILO STRIPE) */
        .stDataFrame {
            border: 1px solid var(--zinc-200);
            border-radius: 12px;
        }
    </style>
    ''', unsafe_allow_html=True)
        
    
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)



def init_db():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS moradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                identidade TEXT,
                cpf TEXT,
                nis TEXT,
                titulo_de_eleitor TEXT,
                telefone TEXT,
                email TEXT,
                data_nascimento TEXT,
                endereco TEXT,
                numero TEXT,
                complemento TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                observacoes TEXT,
                participa_outra_associacao TEXT,
                status_associado TEXT DEFAULT 'Ativo',
                data_cadastro TEXT NOT NULL,
                ultima_atualizacao TEXT,
                editado_por TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE,
                senha TEXT,
                tipo TEXT,
                ativo INTEGER DEFAULT 1
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha, tipo, ativo) VALUES (?, ?, ?, ?)",
                ("admin", "1234", "admin", 1)
            )

        conn.commit()

def buscar_usuario_por_login(usuario: str):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, usuario, senha, tipo, ativo FROM usuarios WHERE usuario = ?",
            (usuario,),
        )
        return cursor.fetchone()  
def criar_usuario(usuario, senha, tipo):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha, tipo, ativo) VALUES (?, ?, ?, 1)",
                (usuario, senha, tipo)
            )
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False


def atualizar_senha(usuario, nova_senha):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE usuarios SET senha = ? WHERE usuario = ?",
                (nova_senha, usuario)
            )
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False
def gerar_csv_download(df):
    return df.to_csv(index=False).encode("utf-8")
                

def limpar_texto(valor: str) -> str:
    return valor.strip() if valor else ""

init_db()
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "tipo_usuario" not in st.session_state:
    st.session_state["tipo_usuario"] = None

def formatar_cpf(cpf):
    numeros = "".join(filter(str.isdigit, cpf or ""))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return cpf

def limpar_numeros(valor: str) -> str:
    """Retorna apenas os dígitos de uma string."""
    return "".join(filter(str.isdigit, str(valor or "")))

def validar_cpf(cpf: str) -> bool:
    """Valida o cálculo dos dígitos verificadores do CPF."""
    cpf = limpar_numeros(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11: return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]): return False
    return True

def validar_email(email: str) -> bool:
    """Validação simples de formato de e-mail."""
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email.lower()) is not None if email else True

def validar_data(data_str: str) -> bool:
    """Verifica se a data é válida e segue o padrão dd/mm/aaaa."""
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_titulo_eleitor(titulo: str) -> bool:
    """Valida se o título tem entre 10 e 12 dígitos (padrão brasileiro)."""
    t = limpar_numeros(titulo)
    return 10 <= len(t) <= 12 if t else True

def consultar_cep(cep: str):
    """Consulta API ViaCEP. Retorna dict com dados ou None."""
    cep_limpo = limpar_numeros(cep)
    if len(cep_limpo) != 8: return None
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=3)
        if response.status_code == 200:
            dados = response.json()
            return dados if "erro" not in dados else None
    except:
        return None
    return None

def buscar_morador_por_cpf(cpf: str):
    """Verifica se o CPF já existe no banco para evitar duplicidade."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM moradores WHERE cpf = ?", (cpf,))
        return cursor.fetchone()


def formatar_telefone(telefone: str) -> str:
    numeros = "".join(filter(str.isdigit, telefone or ""))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return telefone


def validar_campos(nome: str, cpf: str):
    erros = []
    if not limpar_texto(nome):
        erros.append("O nome é obrigatório.")

    cpf_numeros = "".join(filter(str.isdigit, cpf or ""))
    if cpf_numeros and len(cpf_numeros) != 11:
        erros.append("CPF deve ter 11 dígitos.")
    return erros


def inserir_morador(dados: dict):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO moradores (
                nome, identidade, cpf, nis, titulo_de_eleitor, telefone, email, data_nascimento,
                endereco, numero, complemento, bairro, cidade, estado, cep,
                observacoes, participa_outra_associacao, status_associado, data_cadastro, ultima_atualizacao,editad_por 
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                dados["nome"],
                dados["identidade"],
                dados["cpf"],
                dados["nis"],
                dados["titulo_de_eleitor"],
                dados["telefone"],
                dados["email"],
                dados["data_nascimento"],
                dados["endereco"],
                dados["numero"],
                dados["complemento"],
                dados["bairro"],
                dados["cidade"],
                dados["estado"],
                dados["cep"],
                dados["observacoes"],
                dados["participa_outra_associacao"],
                dados["status_associado"],
                dados["data_cadastro"],
                dados["ultima_atualizacao"],
                dados["editado_por"]
            ),
        )
        conn.commit()


def atualizar_morador(morador_id: int, dados: dict):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE moradores SET
                nome = ?, identidade = ?, cpf = ?, nis = ?, titulo_de_eleitor = ?, telefone = ?, email = ?, data_nascimento = ?,
                endereco = ?, numero = ?, complemento = ?, bairro = ?, cidade = ?, estado = ?, cep = ?,
                observacoes = ?, participa_de_outra_associacao = ?, status_associado = ?, ultima_atualizacao = ?, editado_por = ?,
            WHERE id = ?
            ''',
            (
                dados["nome"],
                dados["identidade"],
                dados["cpf"],
                dados["nis"],
                dados["titulo_de_eleitor"],
                dados["telefone"],
                dados["email"],
                dados["data_nascimento"],
                dados["endereco"],
                dados["numero"],
                dados["complemento"],
                dados["bairro"],
                dados["cidade"],
                dados["estado"],
                dados["cep"],
                dados["observacoes"],
                dados["participa_de_outra_associacao"],
                dados["status_associado"],
                dados["ultima_atualizacao"],
                dados["editado_por"],
                morador_id
            ),
        )
        conn.commit()


def excluir_morador(morador_id: int):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM moradores WHERE id = ?", (morador_id,))
        conn.commit()

if not st.session_state["logado"]:
    aplicar_estilo()

    st.markdown(
    f"""
    <div class="info-bar">
        <b>Usuário logado:</b> {st.session_state["usuario_logado"]} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Perfil:</b> {st.session_state["tipo_usuario"]}
    </div>
    """,
    unsafe_allow_html=True
)

    with st.form("form_login"):
        usuario_login = st.text_input("Usuário")
        senha_login = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            usuario_db = buscar_usuario_por_login(usuario_login)

            if usuario_db and usuario_db[4] == 1 and senha_login == usuario_db[2]:
                st.session_state["logado"] = True
                st.session_state["usuario_logado"] = usuario_db[1]
                st.session_state["tipo_usuario"] = usuario_db[3]
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.stop()
def buscar_moradores(termo: str = "", status: str = "Todos") -> pd.DataFrame:
    with closing(get_connection()) as conn:
        query = "SELECT * FROM moradores WHERE 1=1"
        params = []

        if termo:
            query += " AND (nome LIKE ? OR cpf LIKE ? OR identidade LIKE ? OR telefone LIKE ? OR endereco LIKE ?)"
            termo_like = f"%{termo}%"
            params.extend([termo_like, termo_like, termo_like, termo_like, termo_like])

        if status != "Todos":
            query += " AND status_associado = ?"
            params.append(status)

        query += " ORDER BY nome ASC"
        return pd.read_sql_query(query, conn, params=params)


def buscar_por_id(morador_id: int):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM moradores WHERE id = ?", (morador_id,))
        row = cursor.fetchone()
        if not row:
            return None

        colunas = [descricao[0] for descricao in cursor.description]
        return dict(zip(colunas, row))


def exportar_csv(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    output.write(df.to_csv(index=False).encode("utf-8-sig"))
    output.seek(0)
    return output.getvalue()


def gerar_relatorio_html(df: pd.DataFrame, titulo: str = "Relatório de Moradores") -> str:
    total = len(df)
    ativos = len(df[df["status_associado"] == "Ativo"]) if "status_associado" in df.columns else 0
    inativos = len(df[df["status_associado"] == "Inativo"]) if "status_associado" in df.columns else 0

    tabela_html = df.to_html(index=False, classes="tabela", border=0)

    html = f'''
    <html>
    <head>
        <meta charset="utf-8">
        <title>{titulo}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; color: #222; }}
            h1 {{ margin-bottom: 4px; }}
            .info {{ margin-bottom: 20px; }}
            .cards {{ display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
            .card {{ border: 1px solid #ccc; border-radius: 8px; padding: 12px 16px; min-width: 180px; }}
            .tabela {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
            .tabela th, .tabela td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .tabela th {{ background: #f3f3f3; }}
        </style>
    </head>
    <body>
        <h1>{titulo}</h1>
        <div class="info">
            Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
        <div class="cards">
            <div class="card"><strong>Total cadastrados</strong><br>{total}</div>
            <div class="card"><strong>Ativos</strong><br>{ativos}</div>
            <div class="card"><strong>Inativos</strong><br>{inativos}</div>
        </div>
        {tabela_html}
    </body>
    </html>
    '''
    return html

init_db()
aplicar_estilo()

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "logo.jpeg")


st.markdown('<div class="hero-box">', unsafe_allow_html=True)

col_logo, col_texto, col_btn1, col_btn2 = st.columns([1, 4, 1.2, 0.8])

with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

with col_texto:
    st.markdown('<div class="hero-title">Ecopraça Gestão Comunitária</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Cadastro, acompanhamento e relatórios da associação</div>', unsafe_allow_html=True)

with col_btn1:
    if st.session_state["tipo_usuario"] == "admin":
        if st.button("Criar usuário", key="abrir_criar_usuario"):
            st.session_state["mostrar_criar_usuario"] = not st.session_state.get("mostrar_criar_usuario", False)

with col_btn2:
    if st.button("Sair", key="sair_topo"):
        st.session_state["logado"] = False
        st.session_state["usuario_logado"] = None
        st.session_state["tipo_usuario"] = None
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="
        background:#f7faf8;
        border:1px solid #d9e8de;
        padding:10px 14px;
        border-radius:10px;
        margin-bottom:12px;
        font-size:14px;
    ">
        <b>Usuário logado:</b> {st.session_state["usuario_logado"]} &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>Tipo:</b> {st.session_state["tipo_usuario"]}
    </div>
    """,
    unsafe_allow_html=True
)
df_geral = buscar_moradores()
total = len(df_geral)
ativos = len(df_geral[df_geral["status_associado"] == "Ativo"]) if not df_geral.empty else 0
inativos = len(df_geral[df_geral["status_associado"] == "Inativo"]) if not df_geral.empty else 0

csv_dados = gerar_csv_download(df_geral)


m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""
    <div class='metric-card'>
    <div class='metric-icon'>👥</div>
    <div class='metric-label'>Total de Cadastros</div>
    <div class='metric-value'>{total}</div>
    <div class='metric-help'>Base geral de usuários</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class='metric-card'>
    <div class='metric-icon'>✅</div>
    <div class='metric-label'>Associados Ativos</div>
    <div class='metric-value'>{ativos}</div>
    <div class='metric-help'>Cadastros em situação regular</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class='metric-card'>
    <div class='metric-icon'>⚠️</div>
    <div class='metric-label'>Associados Inativos</div>
    <div class='metric-value'>{inativos}</div>
    <div class='metric-help'>Requerem acompanhamento</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
aba1, aba2, aba3, aba4 = st.tabs(["Cadastrar / Editar", "Consultar", "Relatórios", "Conta"])

with aba1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cadastro de morador</div><p class="section-text">Preencha os dados abaixo para cadastrar ou editar um associado.</p>', unsafe_allow_html=True)

    editar_id = st.number_input(
        "ID para edição (deixe 0 para novo cadastro)",
        min_value=0,
        step=1,
        value=0,
    )

    if "mostrar_criar_usuario" not in st.session_state:
        st.session_state["mostrar_criar_usuario"] = False

    if st.session_state["tipo_usuario"] == "admin" and st.session_state["mostrar_criar_usuario"]:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Criar novo usuário")

        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Senha", type="password")
        tipo = st.selectbox("Tipo", ["usuario", "admin"])

        col_btn1, col_btn2 = st.columns([1, 1])

        with col_btn1:
            if st.button("Salvar novo usuário", key="salvar_novo_usuario"):
                if novo_usuario and nova_senha:
                    sucesso = criar_usuario(novo_usuario, nova_senha, tipo)
                    if sucesso:
                        st.success("Usuário criado com sucesso!")
                        st.session_state["mostrar_criar_usuario"] = False
                        st.rerun()
                    else:
                        st.error("Usuário já existe.")
                else:
                    st.warning("Preencha todos os campos.")

        with col_btn2:
            if st.button("Fechar", key="fechar_criar_usuario"):
                st.session_state["mostrar_criar_usuario"] = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    dados_existentes = buscar_por_id(int(editar_id)) if editar_id else None

    with st.form("form_morador"):
        col1, col2, col3 = st.columns(3)

        with col1:
            nome = st.text_input("Nome completo *", value=dados_existentes["nome"] if dados_existentes else "")
            identidade = st.text_input("Identidade (RG)", value=dados_existentes["identidade"] if dados_existentes else "")
            cpf_input = st.text_input(
                "CPF",
                value=dados_existentes["cpf"] if dados_existentes else "",
                placeholder="00000000000"
            )

            cpf = formatar_cpf(cpf_input) if cpf_input else ""
            if cpf:
                st.caption(f"CPF formatado: {formatar_cpf(cpf)}")
            nis = st.text_input("NIS",
                value=dados_existentes["nis"] if dados_existentes else ""
            )

            titulo_de_eleitor = st.text_input(
                "Título de Eleitor",
                value=dados_existentes["titulo_de_eleitor"] if dados_existentes else ""
            )
            outra_associacao = st.radio(
                "Participa de outra associação?",
                ["Não", "Sim"],
                horizontal=True
            )
            data_nascimento = st.text_input(
                "Data de nascimento",
                value=dados_existentes["data_nascimento"] if dados_existentes else "",
                placeholder="dd/mm/aaaa",
            )

        with col2:
            telefone = st.text_input("Telefone", value=dados_existentes["telefone"] if dados_existentes else "")
            email = st.text_input("E-mail", value=dados_existentes["email"] if dados_existentes else "")
            status_associado = st.selectbox(
                "Status",
                ["Ativo", "Inativo"],
                index=0 if not dados_existentes or dados_existentes["status_associado"] == "Ativo" else 1,
            )

        with col3:
            endereco = st.text_input("Endereço", value=dados_existentes["endereco"] if dados_existentes else "")
            numero = st.text_input("Número", value=dados_existentes["numero"] if dados_existentes else "")
            complemento = st.text_input("Complemento", value=dados_existentes["complemento"] if dados_existentes else "")
            bairro = st.text_input("Bairro", value=dados_existentes["bairro"] if dados_existentes else "")

        col4, col5, col6 = st.columns(3)
        with col4:
            cidade = st.text_input("Cidade", value=dados_existentes["cidade"] if dados_existentes else "")
        with col5:
            estado = st.text_input("Estado", value=dados_existentes["estado"] if dados_existentes else "")
        with col6:
            cep = st.text_input("CEP", value=dados_existentes["cep"] if dados_existentes else "")

        observacoes = st.text_area("Observações", value=dados_existentes["observacoes"] if dados_existentes else "")

        salvar = st.form_submit_button("Salvar cadastro")

        if salvar:
            erros = validar_campos(nome, cpf)
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                dados = {
                    "nome": limpar_texto(nome),
                    "identidade": limpar_texto(identidade),
                    "cpf": formatar_cpf(cpf),
                    "telefone": formatar_telefone(telefone),
                    "email": limpar_texto(email),
                    "nis": limpar_texto(nis),
                    "titulo_de_eleitor": limpar_texto(titulo_de_eleitor),
                    "data_nascimento": limpar_texto(data_nascimento),
                    "endereco": limpar_texto(endereco),
                    "numero": limpar_texto(numero),
                    "complemento": limpar_texto(complemento),
                    "bairro": limpar_texto(bairro),
                    "cidade": limpar_texto(cidade),
                    "estado": limpar_texto(estado),
                    "cep": limpar_texto(cep),
                    "observacoes": limpar_texto(observacoes),
                    "status_associado": status_associado,
                    "participa_outra_associacao": outra_associacao,
                    "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "ultima_atualizacao":datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "editado_por": "Admin",
                }

                if dados_existentes:
                    atualizar_morador(int(editar_id), dados)
                    st.success(f"Cadastro ID {int(editar_id)} atualizado com sucesso.")
                else:
                    inserir_morador(dados)
                    st.success("Novo morador cadastrado com sucesso.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Excluir cadastro</div><p class="section-text">Use essa opção com cuidado para remover um registro pelo ID.</p>', unsafe_allow_html=True)

    excluir_id = st.number_input("ID para excluir", min_value=0, step=1)

    if st.session_state["tipo_usuario"] == "admin":
        if st.button("Excluir cadastro"):
            if excluir_id > 0:
                excluir_morador(int(excluir_id))
                st.success("Cadastro excluído com sucesso.")
                st.rerun()
            else:
                st.warning("Informe um ID válido para excluir.")
    else:
        st.info("Somente administradores podem excluir cadastros.")

    st.markdown('</div>', unsafe_allow_html=True)
with aba2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Consulta de moradores</div>'
        '<p class="section-text">Pesquise por nome, CPF, RG, telefone, endereço ou título de eleitor.</p>',
        unsafe_allow_html=True
    )

    termo = st.text_input(
        "Buscar morador",
        placeholder="Digite nome, CPF, RG, telefone, endereço ou título de eleitor",
        key="consulta_termo"
    )

    df_consulta = buscar_moradores()

    if termo:
        termo_busca = termo.lower()

        df_consulta = df_consulta[
            df_consulta.astype(str).apply(
                lambda linha: linha.str.lower().str.contains(termo_busca, na=False).any(),
                axis=1
            )
        ]

    if df_consulta.empty:
        st.info("Nenhum morador encontrado.")
    else:
        st.dataframe(df_consulta, width="stretch", hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)
with aba3:
    st.markdown('<div class="section-title">Relatórios</div><p class="section-text">Visualize os cadastros gerais e exporte os dados da associação.</p>', unsafe_allow_html=True)

    df_relatorio = buscar_moradores()

    if df_relatorio.empty:
        st.info("Ainda não há cadastros para gerar relatório.")
    else:
        st.dataframe(df_relatorio, use_container_width=True, hide_index=True)
        html_relatorio = gerar_relatorio_html(df_relatorio)

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                label="Baixar relatório em HTML",
                data=html_relatorio.encode("utf-8"),
                file_name="relatorio_moradores.html",
                mime="text/html",
            )
            st.download_button(
                label="Baixar relatório em CSV",
                data=exportar_csv(df_relatorio),
                file_name="relatorio_moradores.csv",
                mime="text/csv",
            )
    st.markdown('</div>', unsafe_allow_html=True)
with aba4:
    st.markdown("### 🔐 Alterar senha")

    usuario_logado = st.session_state["usuario_logado"]

    senha_atual = st.text_input("Senha atual", type="password")
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password")

    if st.button("Atualizar senha"):
        usuario_db = buscar_usuario_por_login(usuario_logado)

        if usuario_db:
            senha_correta = usuario_db[2]

            if senha_atual != senha_correta:
                st.error("Senha atual incorreta.")
            elif nova_senha != confirmar_senha:
                st.warning("As senhas não coincidem.")
            elif not nova_senha:
                st.warning("Informe a nova senha.")
            else:
                atualizar_senha(usuario_logado, nova_senha)
                st.success("Senha atualizada com sucesso!")
        else:
            st.error("Usuário não encontrado.")    
    
