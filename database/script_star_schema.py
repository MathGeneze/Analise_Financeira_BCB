import pandas as pd
import sqlite3

# Criando o banco de dados e a conexão
conexao = sqlite3.connect('./database/dados_star_schema.db')
cursor = conexao.cursor()


# / Criando as Tabelas Dimensão
# - Dimensão: Calendário
cursor.execute("""
               CREATE TABLE IF NOT EXISTS dim_calendario(
                   sk_data INTEGER PRIMARY KEY AUTOINCREMENT,
                   data_referencia DATETIME UNIQUE,
                   trimestre INTEGER,
                   ano INTEGER,
                   mes INTEGER,
                   ano_trimestre TEXT
               );
               """)

# - Dimensão: Produto Cartão
cursor.execute("""
               CREATE TABLE IF NOT EXISTS dim_produto_cartao(
                   sk_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                   bandeira TEXT,
                   funcao TEXT,
                   categoria TEXT,
                   modalidade TEXT,
                   
                   -- Restrição única para combinação das 4 colunas
                   UNIQUE(bandeira, funcao, categoria, modalidade)
               );
               """)

# - Dimensão: Canal Acesso (volumetria)
cursor.execute("""
                CREATE TABLE IF NOT EXISTS dim_canal_acesso (
                    sk_canal INTEGER PRIMARY KEY AUTOINCREMENT,
                    canal_acesso TEXT,
                    tipo_transacao TEXT,
                    detalhe_caixa_eletronico TEXT,
                    
                    -- Criamos UMA restrição única para a combinação das 3 colunas
                    UNIQUE(canal_acesso, tipo_transacao, detalhe_caixa_eletronico)
                );
               """)

# - Dimensão: Estado
cursor.execute("""
               CREATE TABLE IF NOT EXISTS dim_estado(
                   sk_estado INTEGER PRIMARY KEY AUTOINCREMENT,
                   estado TEXT NOT NULL UNIQUE
               );
               """)


# / INSERINDO os dados nas tabelas DIMENSÃO
# - Dimensão: Calendário
# cursor.executescript("""
#     -- Anexa o banco de dados de brutos
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS brutos;

#     -- Inserindo os dados no banco de dados
#     INSERT OR IGNORE INTO dim_calendario (data_referencia, trimestre, ano, mes, ano_trimestre)
#     SELECT DISTINCT
#         data_trimestre,
#         trimestre,
#         strftime('%Y', data_trimestre) AS ano,
#         strftime('%m', data_trimestre) AS mes,
#         strftime('%Y', data_trimestre) || '-Q' || trimestre AS ano_trimestre

#     FROM (
#         SELECT data_trimestre, trimestre FROM brutos.stg_estabelecimentos
#         UNION
#         SELECT data_trimestre, trimestre FROM brutos.stg_meios_pagamento
#         UNION
#         SELECT data_trimestre, trimestre FROM brutos.stg_terminais_pos
#         UNION
#         SELECT data_trimestre, trimestre FROM brutos.stg_transacoes_cartao
#         UNION
#         SELECT data_trimestre, trimestre FROM brutos.stg_volumetria_canais
#     )

#     WHERE data_trimestre IS NOT NULL
#     ORDER BY data_trimestre;

#     DETACH DATABASE brutos;


#     """)

# - Dimensão: Produto Cartão
# cursor.executescript("""
#     -- 1. Se conectando com a base de dados
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS dados_brutos;

#     -- 2. Inserir os dados na tabela
#     INSERT OR IGNORE INTO dim_produto_cartao(bandeira, funcao, categoria, modalidade)

#     SELECT DISTINCT
#         bandeira,
#         funcao,
#         COALESCE(categoria, 'Não Aplicável') AS categoria,
#         COALESCE(modalidade, 'Não Aplicável') AS modalidade

#     FROM (
#         -- Busca produtos detalhados da tabale transações
#         SELECT bandeira, funcao, categoria, modalidade
#         FROM dados_brutos.stg_transacoes_cartao

#         UNION

#         -- Busca produtos da tabela de estabelecimentos
#         -- Como esta tabela não tem categoria/modalidade, enviamos NULL para o COALESCE tratar
#         SELECT bandeira, funcao, NULL as categoria, NULL as modalidade
#         FROM dados_brutos.stg_estabelecimentos
#     )

#     -- Ordenação para manter a dimensão organizada por bandeira e função
#     ORDER BY bandeira, funcao, categoria, modalidade;

#     DETACH DATABASE dados_brutos;

#     """)

# - Dimensão: Canal Acesso (volumetria)
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS dados_brutos;

#     INSERT OR IGNORE INTO dim_canal_acesso(canal_acesso, tipo_transacao, detalhe_caixa_eletronico)
#     SELECT DISTINCT
#         canal_acesso,
#         tipo_transacao,
#         detalhe_caixa_eletronico

#     FROM dados_brutos.stg_volumetria_canais
#     ORDER BY canal_acesso;

#     DETACH DATABASE dados_brutos;
#     """)

# - Dimensão: Estado
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS brutos;

#     -- 1. Inserir os estados únicos vindos da tabela de staging
#     INSERT OR IGNORE INTO dim_estado (estado)
#     SELECT DISTINCT estado
#     FROM brutos.stg_terminais_pos
#     WHERE estado IS NOT NULL
#     ORDER BY estado;

#     -- 2. Inserir o registro "Coringa" para dados nacionais
#     INSERT INTO dim_estado (estado) VALUES ('BRASIL - Não Especificado');

#     DETACH DATABASE brutos;

#     """)



# * Criando as Tabelas Fatos
# ! Fato: Volumetria Canais
cursor.execute("""
               CREATE TABLE IF NOT EXISTS fato_volumetria_canais(
                   sk_data INTEGER REFERENCES dim_calendario(sk_data),
                   sk_canal INTEGER REFERENCES dim_canal_acesso(sk_canal),
                   qtd_transacoes INTEGER,
                   valor_transacoes FLOAT
               );
               """)

# ! Fato: Uso Cartões
cursor.execute("""
               CREATE TABLE IF NOT EXISTS fato_uso_cartoes(
                   sk_data INTEGER REFERENCES dim_calendario(sk_data),
                   sk_produto INTEGER REFERENCES dim_produto_cartao(sk_produto),
                   qtd_cartoes_emitidos INTEGER,
                   qtd_cartoes_ativos INTEGER,
                   qtd_transacoes_nacionais INTEGER,
                   valor_transacoes_nacionais FLOAT,
                   qtd_transacoes_internacionais INTEGER,
                   valor_transacoes_internacionais FLOAT
               );
               """)

# ! Fato: Meios de Pagamento
cursor.execute("""
               CREATE TABLE IF NOT EXISTS fato_meios_pagamento(
                   sk_data INTEGER REFERENCES dim_calendario(sk_data),
                   valor_pix FLOAT,
                   valor_ted FLOAT,
                   valor_tec FLOAT,
                   valor_cheque FLOAT,
                   valor_boleto FLOAT,
                   valor_doc FLOAT,
                   valor_cartao_credito FLOAT,
                   valor_cartao_debito FLOAT,
                   valor_cartao_pre_pago FLOAT,
                   valor_trans_intrabancaria FLOAT,
                   valor_convenios FLOAT,
                   valor_debito_direto FLOAT,
                   valor_saques FLOAT,
                   quantidade_pix INTEGER,
                   quantidade_ted INTEGER,
                   quantidade_tec INTEGER,
                   quantidade_cheque INTEGER,
                   quantidade_boleto INTEGER,
                   quantidade_doc INTEGER,
                   quantidade_cartao_credito INTEGER,
                   quantidade_cartao_debito INTEGER,
                   quantidade_cartao_pre_pago INTEGER,
                   quantidade_trans_intrabancaria INTEGER,
                   quantidade_convenios INTEGER,
                   quantidade_debito_direto INTEGER,
                   quantidade_saques INTEGER
               )""")

# ! Fato: Vendas Maquininhas
cursor.execute("""
        CREATE TABLE IF NOT EXISTS fato_vendas_maquininhas(
            sk_data INTEGER REFERENCES dim_calendario(sk_data),
            sk_estado INTEGER REFERENCES dim_estado(sk_estado),
            qtd_terminais_pos INTEGER,
            qtd_terminais_pos_compartilhados INTEGER,
            qtd_terminais_pos_com_chip INTEGER,
            qtd_terminais_pdv INTEGER
        );
        """)

# ! Fato: estabelecimentos
cursor.execute("""
        CREATE TABLE IF NOT EXISTS fato_estabelecimentos(
            sk_data INTEGER REFERENCES dim_calendario (sk_data),
            sk_produto INTEGER REFERENCES dim_produto_cartao (sk_produto),
            qtd_estab_credenciados INTEGER,
            qtd_estab_ativos INTEGER
        );
        """)



# * INSERINDO os dados nas tabelas FATO
# ! Fato: Volumetria Canais
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS dados;
    
#     INSERT INTO fato_volumetria_canais (sk_data, sk_canal, qtd_transacoes, valor_transacoes)
#     SELECT
#         d.sk_data,
#         c.sk_canal,
#         s.qtd_transacoes,
#         s.valor_transacoes
#     FROM dados.stg_volumetria_canais s
    
#     -- 1° JOIN: Busca o ID do tempo
#     JOIN dim_calendario d 
#     ON s.data_trimestre = d.data_referencia
    
#     -- 2° JOIN: Busca o ID do Canal usando a combinação das 3 colunas
#     JOIN dim_canal_acesso c ON
#         s.canal_acesso = c.canal_acesso AND
#         s.tipo_transacao = c.tipo_transacao AND
#         s.detalhe_caixa_eletronico = c.detalhe_caixa_eletronico;
    
#     DETACH DATABASE dados;
    
#     """)

# ! Fato: Uso Cartões
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS dados_brutos;
    
#     INSERT INTO fato_uso_cartoes (
#         sk_data, sk_produto, qtd_cartoes_emitidos, qtd_cartoes_ativos,
#         qtd_transacoes_nacionais, valor_transacoes_nacionais,
#         qtd_transacoes_internacionais, valor_transacoes_internacionais
#     )
    
#     SELECT 
#         d.sk_data,
#         p.sk_produto,
#         s.qtd_cartoes_emitidos,
#         s.qtd_cartoes_ativos,
#         s.qtd_transacoes_nacionais,
#         s.valor_transacoes_nacionais,
#         s.qtd_transacoes_internacionais,
#         s.valor_transacoes_internacionais
    
#     FROM dados_brutos.stg_transacoes_cartao AS s
    
#     -- 1º JOIN: Relaciona a data do trimestre
#     JOIN dim_calendario d ON s.data_trimestre = d.data_referencia
    
#     -- 2º JOIN: Relaciona a combinação única de produto
#     -- Usamos COALESCE para garantir o "de-para" com o texto 'Não Aplicável'
#     JOIN dim_produto_cartao p ON 
#         s.bandeira = p.bandeira AND 
#         s.funcao = p.funcao AND 
#         COALESCE(s.categoria, 'Não Aplicável') = p.categoria AND 
#         COALESCE(s.modalidade, 'Não Aplicável') = p.modalidade;
  
#     DETACH DATABASE dados_brutos;
#     """)

# ! Fato: Meios de Pagamento
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS dados;

#     INSERT INTO fato_meios_pagamento
#     SELECT
#         d.sk_data,
#         s.valor_pix,
#         s.valor_ted,
#         s.valor_tec,
#         s.valor_cheque,
#         s.valor_boleto,
#         s.valor_doc,
#         s.valor_cartao_credito,
#         s.valor_cartao_debito,
#         s.valor_cartao_pre_pago,
#         s.valor_trans_intrabancaria,
#         s.valor_convenios,
#         s.valor_debito_direto,
#         s.valor_saques,
#         s.quantidade_pix,
#         s.quantidade_ted,
#         s.quantidade_tec,
#         s.quantidade_cheque,
#         s.quantidade_boleto,
#         s.quantidade_doc,
#         s.quantidade_cartao_credito,
#         s.quantidade_cartao_debito,
#         s.quantidade_cartao_pre_pago,
#         s.quantidade_trans_intrabancaria,
#         s.quantidade_convenios,
#         s.quantidade_debito_direto,
#         s.quantidade_saques

#     FROM dados.stg_meios_pagamento AS S
#     JOIN dim_calendario AS d ON S.data_trimestre = d.data_referencia;

#     DETACH DATABASE dados;
#     """)

# ! Fato: Vendas Maquininhas
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS dados_brutos;
    
#     INSERT INTO fato_vendas_maquininhas (sk_data, sk_estado, qtd_terminais_pos, qtd_terminais_pos_compartilhados, qtd_terminais_pos_com_chip, qtd_terminais_pdv)
#     SELECT
#         d.sk_data,
#         e.sk_estado,
#         s.qtd_terminais_pos,
#         s.qtd_terminais_pos_compartilhados,
#         s.qtd_terminais_pos_com_chip,
#         s.qtd_terminais_pdv
    
#     FROM dados_brutos.stg_terminais_pos s
#     JOIN dim_calendario d ON s.data_trimestre = d.data_referencia
#     JOIN dim_estado e ON s.estado = e.estado;
    
#     DETACH DATABASE dados_brutos;
    
#     """)

# ! Fato: Estabelecimentos
# cursor.executescript("""
#     ATTACH DATABASE 'database/dados_brutos_bcb.db' AS brutos;
    
#     INSERT INTO fato_estabelecimentos (sk_data, sk_produto, qtd_estab_credenciados, qtd_estab_ativos)
#     SELECT 
#         d.sk_data,
#         p.sk_produto,
#         s.qtd_estab_credenciados,
#         s.qtd_estab_ativos
        
#     FROM brutos.stg_estabelecimentos s
#     JOIN dim_calendario d ON s.data_trimestre = d.data_referencia
    
#     -- Buscamos o produto na dimensão, lembrando que para esta fonte, 
#     -- categoria e modalidade são sempre 'Não Aplicável'
    
#     JOIN dim_produto_cartao p ON 
#         s.bandeira = p.bandeira AND 
#         s.funcao = p.funcao AND 
#         p.categoria = 'Não Aplicável' AND 
#         p.modalidade = 'Não Aplicável';

#     DETACH DATABASE brutos;
    
#     """)




# / Comitando a query SQL
conexao.commit()
