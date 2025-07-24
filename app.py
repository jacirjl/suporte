# app.py
# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
# Define o título da página, o ícone e o layout.
# O layout "wide" faz com que o conteúdo principal ocupe toda a largura da tela.
st.set_page_config(
    page_title="Visualizador de Equipamentos - Municípios PR",
    page_icon="⚡",
    layout="wide"
)


# --- CARREGAMENTO DOS DADOS ---
# Usamos o cache do Streamlit para carregar os dados apenas uma vez,
# o que torna a aplicação muito mais rápida após o primeiro carregamento.
@st.cache_data
def carregar_dados():
    """
    Carrega os dados da planilha 'dados_equipamentos.csv'.
    Retorna um DataFrame do Pandas.
    """
    try:
        # Especificar o tipo de dados da coluna 'Patrimonio' como string durante a leitura
        df = pd.read_csv('inventario_celulares.csv', sep=',', dtype={'Patrimonio': str})
        return df
    except FileNotFoundError:
        # Se o ficheiro não for encontrado, exibe uma mensagem de erro e para a execução.
        st.error("Erro: O ficheiro 'dados_equipamentos.csv' não foi encontrado.")
        st.info("Por favor, certifique-se de que o ficheiro de dados está na mesma pasta que o 'app.py'.")
        return None


# Carrega os dados usando a função cacheada
df = carregar_dados()

# --- INTERFACE DO UTILIZADOR (UI) ---

# Título principal da aplicação
st.title("⚡ Visualizador de Dados de Equipamentos (Otimizado)")
st.markdown("### Uma visão rápida e detalhada dos equipamentos por município do Paraná")

# Só continua a execução se o DataFrame foi carregado com sucesso
if df is not None:
    # --- BARRA LATERAL (SIDEBAR) PARA FILTROS ---
    st.sidebar.header("Filtros")

    # Cria uma lista única e ordenada de municípios a partir da coluna 'Município'
    lista_municipios = sorted(df['Município'].unique())

    # Adiciona uma opção inicial para guiar o utilizador
    opcoes_dropdown = ["Selecione um município..."] + lista_municipios

    # Cria o dropdown (caixa de seleção) na barra lateral
    municipio_selecionado = st.sidebar.selectbox(
        "Escolha um município:",
        options=opcoes_dropdown
    )

    # --- ÁREA DE CONTEÚDO PRINCIPAL ---

    # Verifica se o utilizador já selecionou um município real
    if municipio_selecionado != "Selecione um município...":

        st.header(f"📍 Equipamentos em: {municipio_selecionado}")

        # Filtra o DataFrame para mostrar apenas os dados do município selecionado
        dados_filtrados = df[df['Município'] == municipio_selecionado]

        # Verifica se há dados para o município selecionado
        if not dados_filtrados.empty:
            # --- OTIMIZAÇÃO PRINCIPAL ---
            # Em vez de um loop lento, usamos st.dataframe que é altamente otimizado
            # para exibir grandes volumes de dados de forma rápida e interativa.
            st.dataframe(
                dados_filtrados,
                use_container_width=True,  # Faz a tabela ocupar a largura da página
                hide_index=True  # Oculta o índice numérico à esquerda
            )
            st.success(f"Exibindo {len(dados_filtrados)} registos encontrados.")
        else:
            st.warning("Nenhum dado encontrado para este município.")

    else:
        # Mensagem inicial enquanto nenhum município for selecionado
        st.info("⬅️ Por favor, selecione um município na barra lateral para começar.")

        # Exibe uma visão geral dos dados
        st.subheader("Visão Geral dos Dados")
        total_registros = len(df)
        total_municipios = len(df['Município'].unique())

        col1, col2 = st.columns(2)
        col1.metric("Total de Registos", f"{total_registros}")
        col2.metric("Total de Municípios com Dados", f"{total_municipios}")

        st.markdown("Amostra dos dados carregados:")
        st.dataframe(df.head(10), use_container_width=True)

