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
    page_icon="🖥️",
    layout="wide"
)

# --- ESTILO CSS PARA UMA INTERFACE MODERNA E PROFISSIONAL ---
st.markdown("""
    <style>
        /* --- Fundo e Fonte Principal --- */
        .stApp {
            background-color: #F0F2F6;
            color: #334155; /* Cor de texto principal (cinza-escuro) */
        }
        .main {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }

        /* --- Títulos --- */
        h1 {
            color: #0F172A; /* Azul-marinho muito escuro */
            font-weight: 600;
        }
        h2, h3 {
            color: #1E293B; /* Azul-escuro acinzentado */
            font-weight: 600;
        }

        /* --- Barra Lateral --- */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
            padding: 1rem;
        }

        /* --- "Cards" para conteúdo --- */
        .card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
            border: 1px solid #E2E8F0;
            margin-bottom: 1rem;
        }

        /* --- Grelha de Detalhes do Equipamento --- */
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px 24px;
        }
        .details-grid .item {
            padding: 10px;
            background-color: #F8FAFC;
            border-radius: 8px;
            border-left: 4px solid #3B82F6; /* Destaque azul */
        }
        .details-grid .label {
            font-weight: 600;
            color: #475569;
            font-size: 0.8rem;
            display: block;
            margin-bottom: 2px;
            text-transform: uppercase;
        }
        .details-grid .value {
            color: #1E293B;
            font-size: 1rem;
        }

        /* --- Bordas para campos de entrada --- */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stTextArea"] textarea, 
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 8px;
        }

        /* --- Botão de Submissão --- */
        .stButton button {
            background-color: #2563EB;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            width: 100%;
            transition: background-color 0.3s ease, transform 0.1s ease;
            font-weight: 600;
            font-size: 1rem;
        }
        .stButton button:hover {
            background-color: #1D4ED8;
            transform: translateY(-2px);
        }
        .stButton button:focus {
            box-shadow: 0 0 0 3px #93C5FD;
            outline: none;
        }

        /* --- Mensagens de Sucesso e Aviso --- */
        div[data-testid="stSuccess"], div[data-testid="stWarning"] {
            border-radius: 8px;
            padding: 1rem;
        }

        /* --- Estilo para a lista de chamados --- */
        div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
            align-items: center; /* Alinha verticalmente os itens na linha */
        }
        div[data-testid="stExpander"] hr {
            margin: 0.5rem 0 !important; /* Margem vertical menor para a linha divisória */
        }
        div[data-testid="stExpander"] p {
            margin-bottom: 0.2rem; /* Reduz a margem inferior dos parágrafos na lista */
            line-height: 1.3;
        }
    </style>
    """, unsafe_allow_html=True)


# --- GESTÃO DA BASE DE DADOS DE CHAMADOS ---

def init_chamados_db():
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()

    # Garante que a tabela 'chamados' exista com a estrutura mínima
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

    # Verifica e adiciona colunas faltantes de forma segura
    c.execute("PRAGMA table_info(chamados)")
    existing_columns = [info[1] for info in c.fetchall()]

    if 'status' not in existing_columns:
        c.execute("ALTER TABLE chamados ADD COLUMN status TEXT DEFAULT 'Aberto'")
    if 'solucao' not in existing_columns:
        c.execute("ALTER TABLE chamados ADD COLUMN solucao TEXT DEFAULT ''")

    conn.commit()
    conn.close()


def save_chamado(dados_equipamento, dados_formulario, municipio_col_name):
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
        dados_formulario['relato'],
        'Aberto',  # Status inicial
        ''  # Solução inicial vazia
    )

    c.execute('''
        INSERT INTO chamados (
            timestamp, municipio, imei1, imei2, marca, modelo, capacidade, 
            entrega, local_uso, situacao_equipamento, patrimonio, 
            solicitante_nome, solicitante_telefone, tipo_problema, relato_problema, status, solucao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data_to_insert)

    conn.commit()
    conn.close()


def carregar_chamados_por_municipio(municipio):
    conn = sqlite3.connect('chamados.db')
    try:
        query = "SELECT id as ID, timestamp as Data, patrimonio as Património, tipo_problema as Problema, relato_problema as Relato, status as Status FROM chamados WHERE municipio = ? ORDER BY id DESC"
        df_chamados = pd.read_sql_query(query, conn, params=(municipio,))
        return df_chamados
    except Exception as e:
        st.warning(f"Não foi possível carregar os chamados existentes: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def carregar_detalhes_chamado(chamado_id):
    conn = sqlite3.connect('chamados.db')
    try:
        query = "SELECT * FROM chamados WHERE id = ?"
        df_chamado = pd.read_sql_query(query, conn, params=(chamado_id,))
        return df_chamado.iloc[0] if not df_chamado.empty else None
    finally:
        conn.close()


def update_chamado_details(chamado_id, novo_status, nova_solucao):
    conn = sqlite3.connect('chamados.db')
    c = conn.cursor()
    c.execute("UPDATE chamados SET status = ?, solucao = ? WHERE id = ?", (novo_status, nova_solucao, chamado_id))
    conn.commit()
    conn.close()


init_chamados_db()


# --- CARREGAMENTO DOS DADOS DA BASE DE DADOS DE EQUIPAMENTOS ---
@st.cache_data
def carregar_dados_do_db():
    DB_FILE_PATH = 'chamados.db'
    TABLE_NAME = 'equipamentos'

    if not os.path.exists(DB_FILE_PATH):
        st.error(f"**Base de Dados não encontrada!** Verifique se o ficheiro `{DB_FILE_PATH}` existe.")
        st.info("Por favor, execute primeiro o script `importar_dados.py` para criar a base de dados.")
        return None

    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
        if cursor.fetchone() is None:
            st.error(f"**Tabela de Equipamentos não encontrada!** A tabela `{TABLE_NAME}` não existe na base de dados.")
            st.info("Por favor, execute o script `importar_dados.py` para importar os dados do seu CSV.")
            conn.close()
            return None

        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"**Ocorreu um erro ao ler a base de dados:** {e}")
        st.info("A base de dados pode estar corrompida. Tente executar `importar_dados.py` novamente.")
        return None


df_equipamentos = carregar_dados_do_db()

# --- GESTÃO DE ESTADO ---
if 'editing_chamado_id' not in st.session_state:
    st.session_state.editing_chamado_id = None

# --- MODO DE EDIÇÃO DE CHAMADO ---
if st.session_state.editing_chamado_id is not None:
    chamado_id = st.session_state.editing_chamado_id
    chamado_details = carregar_detalhes_chamado(chamado_id)

    st.title("✍️ Editar Ocorrência")

    if st.button("⬅️ Voltar para a lista"):
        st.session_state.editing_chamado_id = None
        st.rerun()

    if chamado_details is not None:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"Detalhes do Chamado ID: {chamado_id}")

            detalhes_html = "<div class='details-grid'>"
            for label, value in chamado_details.items():
                if label != 'id':
                    detalhes_html += f"<div class='item'><span class='label'>{label}</span> <span class='value'>{value}</span></div>"
            detalhes_html += "</div>"
            st.markdown(detalhes_html, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Registar Solução e Alterar Status")

            status_options = ["Aberto", "Aguardando solução", "Encerrado"]
            try:
                current_status_index = status_options.index(chamado_details['status'])
            except ValueError:
                current_status_index = 0

            novo_status = st.selectbox("Status do Chamado:", options=status_options, index=current_status_index)
            nova_solucao = st.text_area("Descrição da Solução:", value=chamado_details['solucao'], height=150)

            if st.button("Salvar Alterações", use_container_width=True):
                update_chamado_details(chamado_id, novo_status, nova_solucao)
                st.session_state.success_message = f"Chamado {chamado_id} atualizado com sucesso!"
                st.session_state.editing_chamado_id = None
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# --- MODO PRINCIPAL (LISTAGEM E CRIAÇÃO) ---
else:
    st.title("🖥️ Sistema de Registo de Ocorrências")

    if 'success_message' in st.session_state and st.session_state.success_message:
        st.success(st.session_state.success_message, icon="✅")
        st.session_state.success_message = None

    if df_equipamentos is not None:
        municipio_col_name = next((name for name in ['Município', 'Municipio'] if name in df_equipamentos.columns),
                                  None)

        if not municipio_col_name:
            st.error(
                "**ERRO CRÍTICO:** A coluna de Municípios ('Município' ou 'Municipio') não foi encontrada na base de dados.")
        else:
            if st.session_state.get('form_submitted', False):
                st.session_state.form_nome = ""
                st.session_state.form_telefone = ""
                st.session_state.form_tipo_problema = ""
                st.session_state.form_relato = ""
                st.session_state.equipamento_selecionado_index = "Selecione..."
                st.session_state.form_submitted = False

            for key in ['form_nome', 'form_telefone', 'form_tipo_problema', 'form_relato']:
                if key not in st.session_state:
                    st.session_state[key] = ""

            st.sidebar.header("1. Filtro de Busca")


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
                st.header(f"📍 Registos em: {municipio_selecionado}")

                # --- SECÇÃO DE CHAMADOS EXISTENTES (COM BOTÃO EM CADA LINHA) ---
                chamados_existentes = carregar_chamados_por_municipio(municipio_selecionado)
                if not chamados_existentes.empty:
                    with st.expander(f"📖 Ver e Gerir {len(chamados_existentes)} Chamados", expanded=True):
                        for index, row in chamados_existentes.iterrows():
                            col1, col2, col3, col4 = st.columns([1, 2, 3, 1])
                            with col1:
                                st.markdown(f"**ID:** {row['ID']}<br>**Data:** {row['Data'].split(' ')[0]}",
                                            unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"**Património:** {row['Património']}<br>**Status:** {row['Status']}",
                                            unsafe_allow_html=True)
                            with col3:
                                st.markdown(f"**Problema:** {row['Problema']}<br>**Relato:** {row['Relato'][:40]}...",
                                            unsafe_allow_html=True)
                            with col4:
                                if st.button("Editar", key=f"edit_btn_{row['ID']}", use_container_width=True):
                                    st.session_state.editing_chamado_id = row['ID']
                                    st.rerun()
                            st.markdown("---")

                dados_filtrados = df_equipamentos[df_equipamentos[municipio_col_name] == municipio_selecionado].copy()

                if not dados_filtrados.empty:
                    st.header("➕ Abrir Novo Chamado")
                    st.subheader("2. Selecione o Equipamento")

                    equipamento_map = {
                        index: f"Património: {row.get('Patrimonio', 'N/A')} | Modelo: {row.get('Marca', '')} {row.get('Modelo', '')} | Local: {row.get('Local de Uso', '')}"
                        for index, row in dados_filtrados.iterrows()
                    }

                    opcoes_indices = ["Selecione..."] + list(equipamento_map.keys())


                    def format_func(index):
                        return "Selecione..." if index == "Selecione..." else equipamento_map.get(index,
                                                                                                  "Índice inválido")


                    st.selectbox(
                        "Escolha o equipamento para abrir um novo chamado:",
                        options=opcoes_indices,
                        format_func=format_func,
                        key='equipamento_selecionado_index'
                    )

                    indice_selecionado = st.session_state.get('equipamento_selecionado_index')
                    if indice_selecionado is not None and indice_selecionado != "Selecione...":

                        dados_equip_final = dados_filtrados.loc[indice_selecionado]

                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("3. Preencha os Dados do Novo Chamado")

                        st.markdown("**Detalhes do Equipamento Selecionado:**")
                        detalhes_html = "<div class='details-grid'>"
                        for label, value in dados_equip_final.to_dict().items():
                            detalhes_html += f"<div class='item'><span class='label'>{label}</span> <span class='value'>{value}</span></div>"
                        detalhes_html += "</div>"
                        st.markdown(detalhes_html, unsafe_allow_html=True)

                        st.markdown("**Informações do Solicitante e do Problema:**")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.text_input("Nome do Solicitante:", key="form_nome")
                            st.text_input("Telefone de Contacto:", key="form_telefone")
                            st.selectbox(
                                "Tipo de Problema:",
                                ["", "Ajuda aplicativo", "Suporte técnico", "Roubo", "Outros"],
                                key="form_tipo_problema"
                            )
                        with col2:
                            st.text_area("Breve relato do problema:", height=155, key="form_relato")

                        if st.button("✔️ Registar Chamado", use_container_width=True):
                            nome = st.session_state.form_nome
                            telefone = st.session_state.form_telefone
                            tipo_problema = st.session_state.form_tipo_problema
                            relato = st.session_state.form_relato

                            if nome and telefone and tipo_problema and relato:
                                dados_formulario = {
                                    "nome": nome,
                                    "telefone": telefone,
                                    "tipo_problema": tipo_problema,
                                    "relato": relato
                                }
                                patrimonio_str = str(dados_equip_final.get('Patrimonio', 'N/A'))
                                save_chamado(dados_equip_final, dados_formulario, municipio_col_name)

                                st.session_state.success_message = f"Chamado para o equipamento de património **{patrimonio_str}** registado com sucesso!"
                                st.session_state.form_submitted = True
                                st.rerun()
                            else:
                                st.warning("⚠️ Por favor, preencha todos os campos do formulário.", icon="❗")

                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("Nenhum equipamento encontrado para este município.")
            else:
                st.info("⬅️ Comece por selecionar um município na barra lateral para visualizar os equipamentos.")
