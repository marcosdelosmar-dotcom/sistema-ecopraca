import os
import sqlite3
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
    st.markdown(
        '''
        <style>
            .stApp {
                background: linear-gradient(180deg, #dff6e8 0%, #f8fffb 45%, #ffffff 100%);
            }

            .main .block-container {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
    max-width: 980px;
}

            .hero-box {
    background: linear-gradient(135deg, #0b3d2c 0%, #198754 100%);
    border-radius: 20px;
    padding: 20px 24px;
    color: white;
    box-shadow: 0 10px 24px rgba(25, 135, 84, 0.16);
    margin-bottom: 16px;
}

.hero-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 4px;
    line-height: 1.1;
}

.hero-subtitle {
    font-size: 0.95rem;
    opacity: 0.92;
    margin-bottom: 0;
}
            .mini-card {
                background: linear-gradient(180deg, #ffffff 0%, #f6fbf8 100%);
                border: 1px solid #cfe8d8;
                border-radius: 18px;
                padding: 18px;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.07);
                text-align: center;
            }

            .mini-card .label {
                color: #4f6b5b;
                font-size: 0.95rem;
                margin-bottom: 8px;
            }

            .mini-card .value {
                color: #0f5132;
                font-size: 2rem;
                font-weight: 800;
                line-height: 1;
            }

            .section-card {
                background: #ffffff;
                border: 1px solid #d7eadf;
                border-radius: 18px;
                padding: 22px;
                margin-bottom: 18px;
                box-shadow: 0 12px 26px rgba(0, 0, 0, 0.06);
            }

            .info-bar {
                background: linear-gradient(90deg, #e8fff0 0%, #f7fff9 100%);
                border-left: 6px solid #198754;
                border-top: 1px solid #d2f0db;
                border-right: 1px solid #d2f0db;
                border-bottom: 1px solid #d2f0db;
                color: #14532d;
                border-radius: 14px;
                padding: 14px 16px;
                margin-bottom: 16px;
                font-size: 14px;
                box-shadow: 0 6px 16px rgba(25, 135, 84, 0.08);
            }

            .section-title {
                font-size: 1.2rem;
                font-weight: 800;
                color: #0f5132;
                margin-bottom: 8px;
            }

            .section-text {
                color: #5d6f63;
                margin-bottom: 10px;
                font-size: 14px;
            }

            div[data-testid="stTabs"] button[role="tab"] {
                border-radius: 14px;
                padding: 11px 18px;
                margin-right: 8px;
                border: 1px solid #d8ebe0;
                background: #ffffff;
                font-weight: 600;
                transition: all 0.2s ease;
            }
            div[data-testid="stTabs"] button[role="tab"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(25, 135, 84, 0.18);
}
            .hero-box {
    background: linear-gradient(135deg, #0b3d2c 0%, #198754 100%);
    border-radius: 20px;
    padding: 20px 24px;
    color: white;
    box-shadow: 0 10px 24px rgba(25, 135, 84, 0.16);
    margin-bottom: 16px;
}

.hero-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 4px;
    line-height: 1.1;
}

.hero-subtitle {
    font-size: 0.95rem;
    opacity: 0.92;
    margin-bottom: 0;
}

            div[data-testid="stTabs"] button[aria-selected="true"] {
                background: linear-gradient(135deg, #198754 0%, #157347 100%) !important;
                color: white !important;
                border-color: #198754 !important;
                box-shadow: 0 6px 14px rgba(25, 135, 84, 0.18);
            }

            div[data-testid="stForm"] {
                background: #ffffff;
                border-radius: 18px;
                padding: 16px 16px 8px 16px;
                border: 1px solid #dcefe4;
                box-shadow: 0 10px 22px rgba(0, 0, 0, 0.05);
            }

            div.stButton > button,
            div.stDownloadButton > button,
            div[data-testid="stFormSubmitButton"] > button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                border: none !important;
                background: linear-gradient(135deg, #198754 0%, #157347 100%) !important;
                color: white !important;
                padding: 0.72rem 1.1rem !important;
                box-shadow: 0 8px 18px rgba(25, 135, 84, 0.22);
            }

            div.stButton > button:hover,
            div.stDownloadButton > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover {
                background: linear-gradient(135deg, #157347 0%, #0f5132 100%) !important;
                color: white !important;
                transform: translateY(-1px);
            }

            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div {
                border-radius: 12px;
            }
        </style>
        ''',
        unsafe_allow_html=True
    )


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
                data_cadastro TEXT NOT NULL
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

def formatar_cpf(cpf: str) -> str:
    numeros = "".join(filter(str.isdigit, cpf or ""))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return cpf


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
                nome, identidade, cpf, nis, telefone, email, data_nascimento,
                endereco, numero, complemento, bairro, cidade, estado, cep,
                observacoes, participa_outra_associacao, status_associado, data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                dados["nome"],
                dados["identidade"],
                dados["cpf"],
                dados["nis"],
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
            ),
        )
        conn.commit()


def atualizar_morador(morador_id: int, dados: dict):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE moradores SET
                nome = ?, identidade = ?, cpf = ?, telefone = ?, email = ?, data_nascimento = ?,
                endereco = ?, numero = ?, complemento = ?, bairro = ?, cidade = ?, estado = ?, cep = ?,
                observacoes = ?, status_associado = ?
            WHERE id = ?
            ''',
            (
                dados["nome"],
                dados["identidade"],
                dados["cpf"],
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
                dados["status_associado"],
                morador_id,
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


# Interface
init_db()
aplicar_estilo()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "logo.jpeg")

topo_esq, topo_dir1, topo_dir2 = st.columns([6, 1.5, 1])

with topo_dir1:
    if st.session_state["tipo_usuario"] == "admin":
        if st.button("Criar usuário", key="abrir_criar_usuario"):
            st.session_state["mostrar_criar_usuario"] = not st.session_state.get("mostrar_criar_usuario", False)

with topo_dir2:
    if st.button("Sair", key="sair_topo"):
        st.session_state["logado"] = False
        st.session_state["usuario_logado"] = None
        st.session_state["tipo_usuario"] = None
        st.rerun()
st.markdown('<div class="hero-box">', unsafe_allow_html=True)

col_logo, col_texto = st.columns([1, 4])

with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)

with col_texto:
    st.markdown('<div class="hero-title">Sistema de Cadastro</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Associação Ecopraça • Gestão de associados, usuários e relatórios</div>', unsafe_allow_html=True)

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

st.download_button(
    label="📥 Baixar lista de moradores",
    data=csv_dados,
    file_name="moradores.csv",
    mime="text/csv"
)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="mini-card"><div class="label">Total de cadastros</div><div class="value">{total}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="mini-card"><div class="label">Associados ativos</div><div class="value">{ativos}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="mini-card"><div class="label">Associados inativos</div><div class="value">{inativos}</div></div>', unsafe_allow_html=True)

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
            cpf = st.text_input("CPF", value=dados_existentes["cpf"] if dados_existentes else "")
            nis = st.text_input("NIS")
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
with aba3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
