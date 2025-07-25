# importar_dados.py
import pandas as pd
import sqlite3
import os

# --- CONFIGURAÇÕES ---
CSV_FILE_PATH = 'dados_equipamentos.csv'
# Alterado para usar a base de dados de chamados já existente
DB_FILE_PATH = 'chamados.db'
# O nome da tabela para guardar os dados dos equipamentos
TABLE_NAME = 'equipamentos'


def importar_csv_para_sqlite():
    """
    Lê um ficheiro CSV e importa os seus dados para a tabela 'equipamentos'
    dentro da base de dados 'chamados.db'.
    A tabela 'equipamentos' existente será substituída se já existir.
    """
    # Verifica se o ficheiro CSV existe
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Erro: O ficheiro '{CSV_FILE_PATH}' não foi encontrado.")
        print("Por favor, certifique-se de que o ficheiro está na mesma pasta que este script.")
        return

    try:
        # Lê os dados do ficheiro CSV para um DataFrame do Pandas
        print(f"A ler dados de '{CSV_FILE_PATH}'...")
        df = pd.read_csv(CSV_FILE_PATH, sep=';', dtype=str)
        df.columns = df.columns.str.strip()
        print(f"{len(df)} linhas lidas com sucesso.")

        # Conecta-se à base de dados SQLite existente
        print(f"A conectar-se à base de dados '{DB_FILE_PATH}'...")
        conn = sqlite3.connect(DB_FILE_PATH)

        # Usa a função to_sql do Pandas para guardar o DataFrame na base de dados
        # if_exists='replace' irá apagar a tabela antiga e criar uma nova.
        # Isto é útil para garantir que os dados estão sempre atualizados.
        print(f"A importar dados para a tabela '{TABLE_NAME}' dentro de '{DB_FILE_PATH}'...")
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)

        # Fecha a conexão com a base de dados
        conn.close()

        print("\n--- SUCESSO! ---")
        print(f"Os dados foram importados com sucesso para a tabela '{TABLE_NAME}' dentro de '{DB_FILE_PATH}'.")
        print("Agora já pode executar a aplicação principal com 'streamlit run app.py'.")

    except Exception as e:
        print(f"\n--- ERRO ---")
        print(f"Ocorreu um erro durante a importação: {e}")


if __name__ == "__main__":
    importar_csv_para_sqlite()
