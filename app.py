import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Gerenciamento de Banca",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título da aplicação
st.title("💰 Gerenciamento de Banca")

# Inicialização do estado da sessão
if 'initial_value' not in st.session_state:
    st.session_state.initial_value = 50.00
if 'daily_goal' not in st.session_state:
    st.session_state.daily_goal = 10.00
if 'daily_profits' not in st.session_state:
    st.session_state.daily_profits = [None] * 30

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    
    initial_value = st.number_input(
        "Valor Inicial (R$)", 
        min_value=0.0, 
        step=0.01, 
        value=st.session_state.initial_value,
        key="initial_value_input"
    )
    
    daily_goal = st.number_input(
        "Meta Diária (%)", 
        min_value=0.0, 
        step=0.01, 
        value=st.session_state.daily_goal,
        key="daily_goal_input"
    )
    
    if st.button("Atualizar Valores", use_container_width=True):
        st.session_state.initial_value = initial_value
        st.session_state.daily_goal = daily_goal
        st.rerun()
    
    st.divider()
    
    st.header("Adicionar Lucro")
    
    profit_day = st.number_input(
        "Dia", 
        min_value=1, 
        max_value=30, 
        value=1,
        key="profit_day_input"
    )
    
    daily_profit = st.number_input(
        "Lucro do Dia (R$)", 
        step=0.01,
        key="daily_profit_input"
    )
    
    if st.button("Adicionar Lucro", use_container_width=True):
        st.session_state.daily_profits[profit_day-1] = daily_profit
        st.rerun()

# Cálculos
current_value = st.session_state.initial_value
daily_values = [current_value]
total_profit = 0

for i in range(30):
    profit = st.session_state.daily_profits[i]
    if profit is not None:
        current_value += profit
        total_profit += profit
    daily_values.append(current_value)

total_percent = (total_profit / st.session_state.initial_value) * 100 if st.session_state.initial_value > 0 else 0

# Métricas
col1, col2 = st.columns(2)
with col1:
    st.metric("Valor Atual da Banca", f"R$ {daily_values[-1]:.2f}")
with col2:
    st.metric("Lucro Líquido", f"R$ {total_profit:.2f}", f"{total_percent:.2f}%")

# Gráfico de evolução
st.subheader("Evolução da Banca")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(range(31)),
    y=daily_values,
    mode='lines+markers',
    name='Valor da Banca',
    line=dict(color='#3498db', width=3),
    marker=dict(size=6)
))

fig.update_layout(
    xaxis_title="Dia",
    yaxis_title="Valor (R$)",
    hovermode="x unified",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Tabela de resultados
st.subheader("Controle Diário - 30 Dias")

# Preparar dados para a tabela
table_data = []
current_value = st.session_state.initial_value

for i in range(30):
    profit = st.session_state.daily_profits[i]
    daily_goal_value = current_value * (st.session_state.daily_goal / 100)
    
    if profit is not None:
        percent = (profit / current_value) * 100
        current_value += profit
    else:
        percent = 0
    
    table_data.append({
        "Dia": i+1,
        "Valor": f"R$ {current_value:.2f}",
        "Meta": f"R$ {daily_goal_value:.2f}",
        "Lucro do Dia": f"R$ {profit:.2f}" if profit is not None else "R$ -",
        "% da Banca": f"{percent:.2f}%" if profit is not None else "0.00%"
    })

# Exibir tabela
df = pd.DataFrame(table_data)
st.dataframe(df, use_container_width=True, hide_index=True)

# Botão para resetar dados
if st.button("Resetar Dados", type="secondary"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()