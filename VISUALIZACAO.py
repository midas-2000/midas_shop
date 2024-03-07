import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc 
import matplotlib.pyplot as plt

# Configurar o layout da página
st.set_page_config(layout="wide")

dados_conexao = ("Driver={SQL Server};""Server=192.168.11.83,1041;""Database=SFINANCEEM;")
cnnt = pyodbc.connect(dados_conexao)
consultaBD = cnnt.cursor() 

qry = f""" 


DECLARE @PRODUTO AS VARCHAR(MAX)
DECLARE @BANCO AS VARCHAR(MAX)
 
 
SET @PRODUTO = 'REFIN'
SET @BANCO = 'SANTANDER'
 
 
SELECT
EM01_NR_CONTRA                                                                                              AS NMR_CONTRA  
,EM01_VL_CONTRA																								 AS VL_BRUTO					  
,EM01_VL_CONTRA-EM01_VL_IOFCOB-EM01_VL_CONCES-EM01_VL_SEGURO-EM01_VL_OUTVLR-EM01_VL_RETIDO                   AS VL_LIQUIDO
,CAST(EM01_TX_INFORM AS NUMERIC(20,10))/100																AS 	TX_CONTRATO
, CAST(CAST(EM01_DT_ENTRAD  AS  VARCHAR) AS DATE)                                                       AS DATA_CONTRATO
 
 
FROM EM01
JOIN SFINANCEEM.dbo.EM02 ON EM02_CD_PRODUT = EM01_CD_PRODUT
 
WHERE EM01_CD_PRODUT IN (SELECT TABELAS FROM TABELAS_CESSAO WHERE DESCRICAO = @PRODUTO)
 
AND EM01_NR_CONTRA NOT IN (SELECT EM07_NR_CONTRA FROM em07 WHERE EM07_ID_TIPDEB =160)
AND EM01_DT_CONTRA BETWEEN 20240101 AND 20240306
AND EM01_ID_SITUAC = 0
AND EM01_NR_CONTRA NOT IN (SELECT CONTRATOS FROM CONTRATOS_RESERVADOS_CESSAO)


                                """

consultaBD.execute(qry)
cnnt.commit()

df = pd.read_sql(qry, cnnt)


df2 = df.sort_values("DATA_CONTRATO")


# Criar uma seleção de meses na barra lateral do dashboard
month = st.sidebar.selectbox("2024-01-05", df2["DATA_CONTRATO"].unique())

# Filtrar os dados com base no mês selecionado
df2_filtered = df2[df2["DATA_CONTRATO"] == month]

# Exibir o DataFrame filtrado
st.write(df2_filtered)

print(df2.head())

col1, col2 = st.columns(2) # Primeira linha com duas colunas
col3, col4, col5 = st.columns(3) # Segunda linha com três colunas

# Criar o gráfico de faturamento por dia
fig_date = px.bar(df2_filtered, x="DATA_CONTRATO", y="VL_BRUTO", color="TX_CONTRATO", title="Faturamento por dia")

# Exibir o gráfico na primeira coluna
col1.plotly_chart(fig_date, use_container_width=True)

fig_date.show()







