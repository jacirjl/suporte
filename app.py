# app.py
# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Registo de Ocorrências - Municípios PR",
    page_icon="📝",
    layout="wide"
)

# --- ESTILO CSS PARA UMA INTERFACE MODERNA ---
st.markdown("""
    <style>
        /* --- Fundo e Fonte Principal --- */
        .stApp {
            background-color: #F0F2F6;
        }
        .main {
            font-size: 14px;
        }

        /* --- Títulos --- */
        h1, h2, h3 {
            color: #1E293B; /* Azul-escuro acinzentado */
        }

        /* --- Barra Lateral --- */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        /* --- Formulário Principal como um "Card" --- */
        div[data-testid="stForm"] {
            background-color: #FFFFFF;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        /* --- Grelha de Detalhes do Equipamento --- */
        .details-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 20px; /* Espaçamento vertical e horizontal */
            background-color: #F8FAFC;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #E2E8F0;
            margin-bottom: 20px;
        }
        .details-grid .label {
            font-weight: bold;
            color: #475569; /* Cinza-azulado */
        }
        .details-grid .value {
            color: #1E293B;
        }

        /* --- Botão de Submissão --- */
        div[data-testid="stForm"] .stButton button {
            background-color: #2563EB; /* Azul primário */
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            width: 100%;
            transition: background-color 0.3s ease;
            font-weight: bold;
        }
        div[data-testid="stForm"] .stButton button:hover {
            background-color: #1D4ED8; /* Azul mais escuro no hover */
        }
        div[data-testid="stForm"] .stButton button:focus {
            box-shadow: 0 0 0 3px #93C5FD; /* Foco azul claro */
            outline: none;
        }

        /* --- Mensagens de Sucesso e Aviso --- */
        div[data-testid="stSuccess"], div[data-testid="stWarning"] {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


# --- GESTÃO DA BASE DE DADOS DE CHAMADOS ---

def init_chamados_db():
    """
    Inicializa a base de dados de chamados e cria a tabela se não existir.
    """
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            municipio TEXT,
            imei1 TEXT,
            imei2 TEXT,
            marca TEXT,
            modelo TEXT,
            capacidade TEXT,
            entrega TEXT,
            local_uso TEXT,
            situacao_equipamento TEXT,
            patrimonio TEXT,
            solicitante_nome TEXT,
            solicitante_telefone TEXT,
            tipo_problema TEXT,
            relato_problema TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_chamado(dados_equipamento, dados_formulario, municipio_col_name):
    """
    Guarda um novo chamado na base de dados.
    """
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_to_insert = (
        now,
        dados_equipamento[municipio_col_name],
        str(dados_equipamento.get('IMEI1', '')),
        str(dados_equipamento.get('IMEI2', '')),
        dados_equipamento.get('Marca', ''),
        dados_equipamento.get('Modelo', ''),
        dados_equipamento.get('Capacidade', ''),
        dados_equipamento.get('Entrega', ''),
        dados_equipamento.get('Local de Uso', ''),
        dados_equipamento.get('Situação', ''),
        str(dados_equipamento.get('Patrimonio', '')),
        dados_formulario['nome'],
        dados_formulario['telefone'],
        dados_formulario['tipo_problema'],
        dados_formulario['relato']
    )

    c.execute('''
        INSERT INTO chamados (
            timestamp, municipio, imei1, imei2, marca, modelo, capacidade, 
            entrega, local_uso, situacao_equipamento, patrimonio, 
            solicitante_nome, solicitante_telefone, tipo_problema, relato_problema
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data_to_insert)

    conn.commit()
    conn.close()


# Inicializa a base de dados de chamados no início da execução
init_chamados_db()


# --- CARREGAMENTO DOS DADOS DA BASE DE DADOS DE EQUIPAMENTOS ---
@st.cache_data
def carregar_dados_do_db():
    """
    Carrega os dados da tabela 'equipamentos' da base de dados 'chamados.db'.
    """
    DB_FILE_PATH = 'chamados.db'
    TABLE_NAME = 'equipamentos'

    if not os.path.exists(DB_FILE_PATH):
        st.error(f"Erro: A base de dados '{DB_FILE_PATH}' não foi encontrada.")
        st.info("Por favor, execute primeiro o script 'importar_dados.py' para criar e popular a base de dados.")
        return None

    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
        if cursor.fetchone() is None:
            st.error(f"Erro: A tabela '{TABLE_NAME}' não foi encontrada na base de dados.")
            st.info("Por favor, execute o script 'importar_dados.py' para importar os dados do seu CSV.")
            conn.close()
            return None

        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler a base de dados: {e}")
        st.info("Verifique se a base de dados não está corrompida. Tente executar 'importar_dados.py' novamente.")
        return None


df_equipamentos = carregar_dados_do_db()

# --- INTERFACE DO UTILIZADOR (UI) ---

st.title("📝 Sistema de Registo de Ocorrências")
st.markdown("### Selecione o equipamento e registe um novo chamado de serviço")

if 'success_message' in st.session_state and st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = None

if df_equipamentos is not None:
    municipio_col_name = next((name for name in ['Município', 'Municipio'] if name in df_equipamentos.columns), None)

    if not municipio_col_name:
        st.error(
            "ERRO CRÍTICO: A coluna de Municípios ('Município' ou 'Municipio') não foi encontrada na base de dados.")
    else:
        if 'form_submitted' in st.session_state and st.session_state.form_submitted:
            st.session_state.equipamento_selecionado_index = "Selecione..."
            st.session_state.form_submitted = False

        st.sidebar.header("1. Filtro por Município")


        def on_municipio_change():
            if 'equipamento_selecionado_index' in st.session_state:
                st.session_state.equipamento_selecionado_index = "Selecione..."


        lista_municipios = ["Selecione..."] + sorted(df_equipamentos[municipio_col_name].unique())
        st.sidebar.selectbox(
            "Município:",
            options=lista_municipios,
            on_change=on_municipio_change,
            key='municipio_selecionado_key'
        )

        if st.session_state.get(
                'municipio_selecionado_key') and st.session_state.municipio_selecionado_key != "Selecione...":
            municipio_selecionado = st.session_state.municipio_selecionado_key
            st.header(f"📍 Equipamentos em: {municipio_selecionado}")
            dados_filtrados = df_equipamentos[df_equipamentos[municipio_col_name] == municipio_selecionado].copy()

            if not dados_filtrados.empty:
                st.markdown("---")
                st.subheader("2. Selecione o Equipamento")

                equipamento_map = {
                    index: f"Património: {row.get('Patrimonio', 'N/A')} | Modelo: {row.get('Marca', '')} {row.get('Modelo', '')} | Local: {row.get('Local de Uso', '')}"
                    for index, row in dados_filtrados.iterrows()
                }

                opcoes_indices = ["Selecione..."] + list(equipamento_map.keys())


                def format_func(index):
                    return "Selecione..." if index == "Selecione..." else equipamento_map.get(index, "Índice inválido")


                st.selectbox(
                    "Escolha o equipamento para abrir o chamado:",
                    options=opcoes_indices,
                    format_func=format_func,
                    key='equipamento_selecionado_index'
                )

                if st.session_state.get(
                        'equipamento_selecionado_index') and st.session_state.equipamento_selecionado_index != "Selecione...":

                    indice_selecionado = st.session_state.equipamento_selecionado_index
                    dados_equip_final = dados_filtrados.loc[indice_selecionado]

                    st.markdown("---")
                    st.subheader("3. Preencha os Dados do Chamado")

                    with st.form(key=f"form_{indice_selecionado}", clear_on_submit=True):
                        st.markdown("**Detalhes do Equipamento Selecionado:**")

                        # Constrói uma grelha HTML para exibir os detalhes
                        detalhes_html = "<div class='details-grid'>"
                        for label, value in dados_equip_final.to_dict().items():
                            detalhes_html += f"<div><span class='label'>{label}:</span> <span class='value'>{value}</span></div>"
                        detalhes_html += "</div>"
                        st.markdown(detalhes_html, unsafe_allow_html=True)

                        nome = st.text_input("Nome do Solicitante:")
                        telefone = st.text_input("Telefone de Contacto:")
                        tipo_problema = st.selectbox(
                            "Tipo de Problema:",
                            ["", "Ajuda aplicativo", "Suporte técnico", "Roubo", "Outros"]
                        )
                        relato = st.text_area("Breve relato do problema:", height=100)

                        submitted = st.form_submit_button("✔️ Registar Chamado")

                        if submitted:
                            if nome and telefone and tipo_problema and relato:
                                dados_formulario = {
                                    "nome": nome,
                                    "telefone": telefone,
                                    "tipo_problema": tipo_problema,
                                    "relato": relato
                                }
                                patrimonio_str = str(dados_equip_final.get('Patrimonio', 'N/A'))
                                save_chamado(dados_equip_final, dados_formulario, municipio_col_name)

                                st.session_state.success_message = f"✅ Chamado para o equipamento de património **{patrimonio_str}** registado com sucesso!"
                                st.session_state.form_submitted = True
                                st.rerun()
                            else:
                                st.warning("⚠️ Por favor, preencha todos os campos do formulário.")
            else:
                st.warning("Nenhum equipamento encontrado para este município.")
        else:
            st.info("⬅️ Comece por selecionar um município na barra lateral.")
