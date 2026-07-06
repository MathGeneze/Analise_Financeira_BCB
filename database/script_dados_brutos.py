import sqlite3
import pandas as pd

conexao = sqlite3.connect('./database/dados_brutos_bcb.db')
cursor = conexao.cursor()

# / Tabela: stg_estabelecimentos
# ! stg = staging (fase onde os dados são carregados de forma bruta antes do tratamento)
cursor.execute("""
               CREATE TABLE IF NOT EXISTS stg_estabelecimentos(
                   data_trimestre DATETIME NOT NULL,
                   trimestre INTEGER NOT NULL,
                   bandeira text NOT NULL,
                   funcao text NOT NULL,
                   qtd_estab_credenciados INTEGER NOT NULL,
                   qtd_estab_ativos INTEGER NOT NULL

               )""")

# / Tabela: stg_meios_pagamento
cursor.execute("""
               CREATE TABLE IF NOT EXISTS stg_meios_pagamento(
                   data_trimestre DATETIME NOT NULL,
                   trimestre INTEGER NOT NULL,
                   valor_pix FLOAT NOT NULL,
                   valor_ted FLOAT NOT NULL,
                   valor_tec FLOAT NOT NULL,
                   valor_cheque FLOAT NOT NULL,
                   valor_boleto FLOAT NOT NULL,
                   valor_doc FLOAT NOT NULL,
                   valor_cartao_credito FLOAT NOT NULL,
                   valor_cartao_debito FLOAT NOT NULL,
                   valor_cartao_pre_pago FLOAT NOT NULL,
                   valor_trans_intrabancaria FLOAT NOT NULL,
                   valor_convenios FLOAT NOT NULL,
                   valor_debito_direto FLOAT NOT NULL,
                   valor_saques FLOAT NOT NULL,
                   quantidade_pix INTEGER NOT NULL,
                   quantidade_ted INTEGER NOT NULL,
                   quantidade_tec INTEGER NOT NULL,
                   quantidade_cheque INTEGER NOT NULL,
                   quantidade_boleto INTEGER NOT NULL,
                   quantidade_doc INTEGER NOT NULL,
                   quantidade_cartao_credito INTEGER NOT NULL,
                   quantidade_cartao_debito INTEGER NOT NULL,
                   quantidade_cartao_pre_pago INTEGER NOT NULL,
                   quantidade_trans_intrabancaria INTEGER NOT NULL,
                   quantidade_convenios INTEGER NOT NULL,
                   quantidade_debito_direto INTEGER NOT NULL,
                   quantidade_saques INTEGER NOT NULL
               )""")

# / Tabela: stg_terminais_pos
cursor.execute("""
               CREATE TABLE IF NOT EXISTS stg_terminais_pos(
                   data_trimestre DATETIME NOT NULL,
                   trimestre INTEGER NOT NULL,
                   estado TEXT NOT NULL,
                   qtd_terminais_pos INTEGER NOT NULL,
                   qtd_terminais_pos_compartilhados INTEGER NOT NULL,
                   qtd_terminais_pos_com_chip INTEGER NOT NULL,
                   qtd_terminais_pdv INTEGER NOT NULL
               )""")

# / Tabela: stg_transacoes_cartao
cursor.execute("""
               CREATE TABLE IF NOT EXISTS stg_transacoes_cartao(
                   data_trimestre DATETIME NOT NULL,
                   trimestre INTEGER NOT NULL,
                   bandeira TEXT NOT NULL,
                   funcao TEXT NOT NULL,
                   categoria TEXT NOT NULL,
                   modalidade TEXT NOT NULL,
                   qtd_cartoes_emitidos INTEGER NOT NULL,
                   qtd_cartoes_ativos INTEGER NOT NULL,
                   qtd_transacoes_nacionais INTEGER NOT NULL,
                   valor_transacoes_nacionais FLOAT NOT NULL,
                   qtd_transacoes_internacionais INTEGER NOT NULL,
                   valor_transacoes_internacionais FLOAT NOT NULL
               )""")

# / Tabela: stg_volumetria_canais
cursor.execute("""
               CREATE TABLE IF NOT EXISTS stg_volumetria_canais(
                   data_trimestre DATETIME NOT NULL,
                   trimestre INTEGER NOT NULL,
                   canal_acesso TEXT NOT NULL,
                   tipo_transacao TEXT NOT NULL,
                   detalhe_caixa_eletronico TEXT NOT NULL,
                   qtd_transacoes INTEGER NOT NULL,
                   valor_transacoes FLOAT NOT NULL
               )""")


# * Adicionando os dados
def adicionando_dados(caminho=str):
    # Carregando o arquivo CSV
    df = pd.read_csv(f'./data/{caminho}.csv', sep=';')

    # Adicionando os dados nas tabelas
    df.to_sql(caminho, conexao, if_exists='append', index=False)

    # Validando a carga de dados
    print(
        f'Carga concluída! \nTabela: {caminho} - Linhas inseridas: {len(df)}')

lista = ['stg_estabelecimentos', 'stg_meios_pagamento',
         'stg_terminais_pos', 'stg_transacoes_cartao', 'stg_volumetria_canais']

for arquivos in lista:
    adicionando_dados(arquivos)


conexao.commit()
