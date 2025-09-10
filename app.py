import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Gestão de Banca",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar o estado da sessão
if 'initial_value' not in st.session_state:
    st.session_state.initial_value = 55.00
    
if 'daily_goal' not in st.session_state:
    st.session_state.daily_goal = 10.00
    
if 'daily_profits' not in st.session_state:
    st.session_state.daily_profits = [None] * 30
    
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Aplicar modo escuro se ativado
if st.session_state.dark_mode:
    dark_mode_css = """
    <style>
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    .css-18e3th9 {
        background-color: #1a1a1a;
    }
    .css-1d391kg {
        background-color: #2d2d2d;
    }
    .st-bb {
        background-color: #2d2d2d;
    }
    .st-at {
        background-color: #3d3d3d;
    }
    .st-bh {
        background-color: #3d3d3d;
    }
    .st-bx {
        background-color: #3d3d3d;
    }
    .stNumberInput input {
        background-color: #3d3d3d;
        color: #e0e0e0;
    }
    .stDataFrame {
        background-color: #2d2d2d;
        color: #e0e0e0;
    }
    .stMetric {
        background-color: #2d2d2d;
        color: #e0e0e0;
    }
    </style>
    """
    st.markdown(dark_mode_css, unsafe_allow_html=True)

# Título da aplicação
st.title("💰 Gestão de Banca")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    
    # Toggle para modo escuro
    dark_mode = st.toggle("Modo Escuro", value=st.session_state.dark_mode, key="dark_mode_toggle")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
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
        value=0.0,
        key="daily_profit_input"
    )
    
    if st.button("Adicionar Lucro", use_container_width=True):
        st.session_state.daily_profits[profit_day-1] = daily_profit
        st.rerun()

# Cálculos dos valores
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

# Exibir métricas
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
    height=400,
    plot_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'rgba(255,255,255,1)',
    paper_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'rgba(255,255,255,1)',
    font=dict(color='#e0e0e0' if st.session_state.dark_mode else '#333333')
)

st.plotly_chart(fig, use_container_width=True)

# Tabela de resultados
st.subheader("Controle Diário - 30 Dias")

# Preparar dados para a tabela
table_data = []
current_value_calc = st.session_state.initial_value

for i in range(30):
    profit = st.session_state.daily_profits[i]
    daily_goal_value = current_value_calc * (st.session_state.daily_goal / 100)
    
    if profit is not None:
        percent = (profit / current_value_calc) * 100
        current_value_calc += profit
    else:
        percent = 0
    
    # Determinar cor do texto baseado no valor
    profit_color = "#27ae60" if profit and profit > 0 else "#e74c3c" if profit and profit < 0 else "inherit"
    percent_color = "#27ae60" if percent > 0 else "#e74c3c" if percent < 0 else "inherit"
    
    table_data.append({
        "Dia": i+1,
        "Valor": f"R$ {current_value_calc:.2f}",
        "Meta": f"R$ {daily_goal_value:.2f}",
        "Lucro do Dia": f"R$ {profit:.2f}" if profit is not None else "R$ -",
        "% da Banca": f"{percent:.2f}%" if profit is not None else "0.00%",
        "profit_color": profit_color,
        "percent_color": percent_color
    })

# Criar DataFrame
df = pd.DataFrame(table_data)

# Estilizar a tabela
def color_profit(val):
    color = "#27ae60" if val.startswith("R$") and float(val[3:]) > 0 else "#e74c3c" if val.startswith("R$") and float(val[3:]) < 0 else "inherit"
    return f'color: {color}; font-weight: bold;'

def color_percent(val):
    if val == "0.00%" or val == "R$ -":
        return ''
    percent_val = float(val[:-1])
    color = "#27ae60" if percent_val > 0 else "#e74c3c"
    return f'color: {color}; font-weight: bold;'

# Aplicar estilos
styled_df = df.style.applymap(color_profit, subset=['Lucro do Dia'])\
                   .applymap(color_percent, subset=['% da Banca'])\
                   .set_properties(**{'background-color': '#2d2d2d', 'color': '#e0e0e0'} if st.session_state.dark_mode else {'background-color': '#ffffff', 'color': '#000000'})

# Exibir tabela
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Botão para resetar dados
if st.button("Resetar Dados", type="secondary"):
    for key in st.session_state.keys():
        if key not in ['dark_mode']:
            del st.session_state[key]
    st.rerun()
