# app.py
# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Registo de Ocorrências - Municípios PR",
    page_icon="📝",
    layout="wide"
)

# --- ESTILO CSS PARA AJUSTAR A FONTE ---
st.markdown("""
    <style>
    .main, .stTextInput, .stTextArea, .stSelectbox {
        font-size: 14px !important;
    }
    .stMetric {
        font-size: 16px !important;
    }
    h3 {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- GESTÃO DA BASE DE DADOS SQLITE ---

def init_db():
    """
    Inicializa a base de dados SQLite e cria a tabela 'chamados' se não existir.
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


# Inicializa a base de dados no início da execução
init_db()


# --- CARREGAMENTO DOS DADOS DA PLANILHA ---
@st.cache_data
def carregar_dados():
    """
    Carrega os dados da planilha 'dados_equipamentos.csv', usando ponto e vírgula como separador.
    """
    try:
        df = pd.read_csv('dados_equipamentos.csv', sep=';', dtype=str)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error("Erro: O ficheiro 'dados_equipamentos.csv' não foi encontrado.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar o ficheiro CSV: {e}")
        return None


df_equipamentos = carregar_dados()

# --- INTERFACE DO UTILIZADOR (UI) ---

st.title("📝 Sistema de Registo de Ocorrências")
st.markdown("### Selecione o equipamento e registe um novo chamado de serviço")

if df_equipamentos is not None:
    municipio_col_name = next((name for name in ['Município', 'Municipio'] if name in df_equipamentos.columns), None)

    if not municipio_col_name:
        st.error("ERRO CRÍTICO: A coluna de Municípios ('Município' ou 'Municipio') não foi encontrada no ficheiro.")
    else:
        # --- BARRA LATERAL (SIDEBAR) PARA FILTROS ---
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

        # --- ÁREA DE CONTEÚDO PRINCIPAL ---
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

                # --- PASSO 3: FORMULÁRIO DE REGISTO ---
                if st.session_state.get(
                        'equipamento_selecionado_index') and st.session_state.equipamento_selecionado_index != "Selecione...":

                    indice_selecionado = st.session_state.equipamento_selecionado_index
                    dados_equip_final = dados_filtrados.loc[indice_selecionado]

                    st.markdown("---")
                    st.subheader("3. Preencha os Dados do Chamado")

                    with st.form(key=f"form_{indice_selecionado}", clear_on_submit=True):
                        st.markdown("**Detalhes do Equipamento Selecionado:**")

                        # Exibe todos os campos do equipamento em duas colunas
                        col1, col2 = st.columns(2)
                        # Converte a série de dados para um dicionário para iterar
                        detalhes = dados_equip_final.to_dict()
                        # Divide os itens do dicionário para as duas colunas
                        mid_point = len(detalhes) // 2

                        with col1:
                            for i, (label, value) in enumerate(detalhes.items()):
                                if i < mid_point:
                                    st.text(f"{label}: {value}")
                        with col2:
                            for i, (label, value) in enumerate(detalhes.items()):
                                if i >= mid_point:
                                    st.text(f"{label}: {value}")

                        st.markdown("---")  # Linha divisória

                        nome = st.text_input("Nome do Solicitante:")
                        telefone = st.text_input("Telefone de Contacto:")
                        tipo_problema = st.selectbox(
                            "Tipo de Problema:",
                            ["", "Ajuda aplicativo", "Suporte técnico", "Roubo", "Outros"]
                        )
                        relato = st.text_area("Breve relato do problema:")

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
                                st.success(
                                    f"✅ Chamado para o equipamento de património **{patrimonio_str}** registado com sucesso!")

                                st.session_state.equipamento_selecionado_index = "Selecione..."
                                st.rerun()
                            else:
                                st.warning("⚠️ Por favor, preencha todos os campos do formulário.")
            else:
                st.warning("Nenhum equipamento encontrado para este município.")
        else:
            st.info("⬅️ Comece por selecionar um município na barra lateral.")
