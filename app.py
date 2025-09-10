import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Gestão do Capital",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar o estado da sessão
if 'initial_value' not in st.session_state:
    st.session_state.initial_value = 55.00
    
if 'daily_goal' not in st.session_state:
    st.session_state.daily_goal = 10.00
    
if 'stop_loss' not in st.session_state:
    st.session_state.stop_loss = 5.00  # Stop loss padrão de 5%
    
if 'daily_profits' not in st.session_state:
    st.session_state.daily_profits = [None] * 30
    
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
    
if 'editing_day' not in st.session_state:
    st.session_state.editing_day = None

# Aplicar modo escuro se ativado
if st.session_state.dark_mode:
    dark_mode_css = """
    <style>
    :root {
        --primary-bg: #1a1a1a;
        --secondary-bg: #2d2d2d;
        --tertiary-bg: #3d3d3d;
        --primary-text: #e0e0e0;
        --border-color: #444444;
    }
    
    .stApp {
        background-color: var(--primary-bg);
        color: var(--primary-text);
    }
    
    .css-18e3th9, .css-1d391kg, .st-bb, .st-at, .st-bh, .st-bx {
        background-color: var(--secondary-bg) !important;
    }
    
    .stNumberInput input, .stTextInput input, .stSelectbox select {
        background-color: var(--tertiary-bg) !important;
        color: var(--primary-text) !important;
        border-color: var(--border-color) !important;
    }
    
    .stDataFrame {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-text) !important;
    }
    
    .stMetric {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-text) !important;
    }
    
    .stMetric label {
        color: var(--primary-text) !important;
    }
    
    .stButton button {
        background-color: #2980b9 !important;
        color: white !important;
    }
    
    .stButton button:hover {
        background-color: #1d6fa5 !important;
    }
    
    .css-1y4v5go {
        background-color: var(--secondary-bg) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-bg) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--primary-text) !important;
    }
    
    .stop-loss-warning {
        background-color: #8B0000 !important;
        color: white !important;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .stop-loss-safe {
        background-color: #006400 !important;
        color: white !important;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """
    st.markdown(dark_mode_css, unsafe_allow_html=True)
else:
    light_mode_css = """
    <style>
    .stop-loss-warning {
        background-color: #FFCCCB !important;
        color: #8B0000 !important;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #8B0000;
    }
    
    .stop-loss-safe {
        background-color: #DFF0D8 !important;
        color: #006400 !important;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #006400;
    }
    </style>
    """
    st.markdown(light_mode_css, unsafe_allow_html=True)

# Título da aplicação
st.title("💰 Gestão do Capital")

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
    
    stop_loss = st.number_input(
        "Stop Loss Diário (%)", 
        min_value=0.0, 
        max_value=100.0,
        step=0.01, 
        value=st.session_state.stop_loss,
        key="stop_loss_input",
        help="Percentual máximo de perda permitido por dia"
    )
    
    if st.button("Atualizar Configurações", use_container_width=True):
        st.session_state.initial_value = initial_value
        st.session_state.daily_goal = daily_goal
        st.session_state.stop_loss = stop_loss
        st.rerun()
    
    st.divider()
    
    st.header("Adicionar/Editar Lucro")
    
    profit_day = st.number_input(
        "Dia", 
        min_value=1, 
        max_value=30, 
        value=1,
        key="profit_day_input"
    )
    
    # Mostrar valor atual se já existir
    current_profit = st.session_state.daily_profits[profit_day-1]
    profit_value = current_profit if current_profit is not None else 0.0
    
    daily_profit = st.number_input(
        "Lucro do Dia (R$)", 
        step=0.01,
        value=profit_value,
        key="daily_profit_input"
    )
    
    # Calcular valor atual da banca no dia selecionado
    current_value_at_day = st.session_state.initial_value
    for i in range(profit_day-1):
        profit = st.session_state.daily_profits[i]
        if profit is not None:
            current_value_at_day += profit
    
    # Calcular stop loss em valor absoluto
    stop_loss_value = current_value_at_day * (stop_loss / 100)
    
    st.info(f"Valor da banca no dia {profit_day}: R$ {current_value_at_day:.2f}")
    st.info(f"Stop Loss máximo: R$ {abs(stop_loss_value):.2f} ({stop_loss}%)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Salvar", use_container_width=True):
            # Verificar se o prejuízo excede o stop loss
            if daily_profit < 0 and abs(daily_profit) > stop_loss_value:
                st.error(f"❌ Prejuízo excede o stop loss! Máximo permitido: R$ {abs(stop_loss_value):.2f}")
            else:
                st.session_state.daily_profits[profit_day-1] = daily_profit
                st.session_state.editing_day = None
                st.rerun()
    with col2:
        if st.button("Limpar", use_container_width=True):
            st.session_state.daily_profits[profit_day-1] = None
            st.rerun()

# Cálculos dos valores
current_value = st.session_state.initial_value
daily_values = [current_value]
total_profit = 0
stop_loss_triggered = False
stop_loss_day = None

for i in range(30):
    profit = st.session_state.daily_profits[i]
    daily_goal_value = current_value * (st.session_state.daily_goal / 100)
    stop_loss_value_day = current_value * (st.session_state.stop_loss / 100)
    
    # Verificar se o stop loss foi violado
    if profit is not None and profit < 0 and abs(profit) > stop_loss_value_day:
        stop_loss_triggered = True
        stop_loss_day = i + 1
    
    if profit is not None:
        current_value += profit
        total_profit += profit
    daily_values.append(current_value)

total_percent = (total_profit / st.session_state.initial_value) * 100 if st.session_state.initial_value > 0 else 0

# Exibir alerta de stop loss se violado
if stop_loss_triggered:
    st.markdown(f'<div class="stop-loss-warning">⚠️ <b>ALERTA:</b> Stop Loss violado no Dia {stop_loss_day}! Reveja sua estratégia.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="stop-loss-safe">✅ Stop Loss respeitado em todos os dias</div>', unsafe_allow_html=True)

# Exibir métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Valor Inicial", f"R$ {st.session_state.initial_value:.2f}")
with col2:
    st.metric("Valor Atual", f"R$ {daily_values[-1]:.2f}")
with col3:
    st.metric("Lucro Líquido", f"R$ {total_profit:.2f}", f"{total_percent:.2f}%")
with col4:
    st.metric("Stop Loss", f"{st.session_state.stop_loss}%")

# Gráfico de evolução
st.subheader("Evolução da Banca")
fig = go.Figure()

# Linha principal da evolução
fig.add_trace(go.Scatter(
    x=list(range(31)),
    y=daily_values,
    mode='lines+markers',
    name='Valor da Banca',
    line=dict(color='#3498db', width=3),
    marker=dict(size=6)
))

# Adicionar linha de stop loss dinâmica
stop_loss_values = [st.session_state.initial_value]
for i in range(30):
    current_val = stop_loss_values[-1]
    stop_loss_val = current_val * (1 - st.session_state.stop_loss / 100)
    stop_loss_values.append(stop_loss_val)

fig.add_trace(go.Scatter(
    x=list(range(31)),
    y=stop_loss_values,
    mode='lines',
    name='Limite Stop Loss',
    line=dict(color='#e74c3c', width=2, dash='dash'),
    opacity=0.7
))

fig.update_layout(
    xaxis_title="Dia",
    yaxis_title="Valor (R$)",
    hovermode="x unified",
    height=400,
    plot_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'rgba(255,255,255,1)',
    paper_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'rgba(255,255,255,1)',
    font=dict(color='#e0e0e0' if st.session_state.dark_mode else '#333333'),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# Tabela de resultados com opção de edição
st.subheader("Controle Diário - 30 Dias")

# Preparar dados para a tabela
table_data = []
current_value_calc = st.session_state.initial_value

for i in range(30):
    profit = st.session_state.daily_profits[i]
    daily_goal_value = current_value_calc * (st.session_state.daily_goal / 100)
    stop_loss_value_day = current_value_calc * (st.session_state.stop_loss / 100)
    
    if profit is not None:
        percent = (profit / current_value_calc) * 100
        current_value_calc += profit
        
        # Verificar violação do stop loss
        stop_loss_violated = profit < 0 and abs(profit) > stop_loss_value_day
    else:
        percent = 0
        stop_loss_violated = False
    
    table_data.append({
        "Dia": i+1,
        "Valor": f"R$ {current_value_calc:.2f}",
        "Meta": f"R$ {daily_goal_value:.2f}",
        "Lucro do Dia": f"R$ {profit:.2f}" if profit is not None else "R$ -",
        "% da Banca": f"{percent:.2f}%" if profit is not None else "0.00%",
        "Stop Loss": f"R$ {stop_loss_value_day:.2f}",
        "Status": "❌ Violado" if stop_loss_violated else "✅ Respeitado" if profit is not None else "⏳ Pendente"
    })

# Criar DataFrame
df = pd.DataFrame(table_data)

# Função para aplicar estilos condicionais
def highlight_cells(val):
    if val.startswith("R$") and val != "R$ -":
        profit_val = float(val[3:])
        color = "#27ae60" if profit_val > 0 else "#e74c3c" if profit_val < 0 else "inherit"
        return f'color: {color}; font-weight: bold;'
    return ''

def highlight_percent(val):
    if val.endswith("%") and val != "0.00%":
        percent_val = float(val[:-1])
        color = "#27ae60" if percent_val > 0 else "#e74c3c" if percent_val < 0 else "inherit"
        return f'color: {color}; font-weight: bold;'
    return ''

def highlight_status(val):
    if val == "❌ Violado":
        return 'color: #e74c3c; font-weight: bold;'
    elif val == "✅ Respeitado":
        return 'color: #27ae60; font-weight: bold;'
    return ''

# Aplicar estilos
styled_df = df.style\
    .applymap(highlight_cells, subset=['Lucro do Dia'])\
    .applymap(highlight_percent, subset=['% da Banca'])\
    .applymap(highlight_status, subset=['Status'])

# Exibir tabela
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Botões de edição rápida
st.subheader("Edição Rápida por Dia")
cols = st.columns(6)
for i in range(30):
    with cols[i % 6]:
        day = i + 1
        profit = st.session_state.daily_profits[i]
        button_label = f"Dia {day}" + (f": {profit:.2f}" if profit is not None else "")
        button_type = "primary" if profit is not None else "secondary"
        
        if st.button(button_label, key=f"edit_{i}", use_container_width=True, type=button_type):
            st.session_state.profit_day_input = day
            st.session_state.daily_profit_input = profit if profit is not None else 0.0
            st.rerun()

# Botão para resetar todos os dados
if st.button("Resetar Todos os Dados", type="secondary"):
    for key in st.session_state.keys():
        if key not in ['dark_mode', 'stop_loss']:
            del st.session_state[key]
    st.rerun()

# Informações de uso
with st.expander("ℹ️ Como usar - Stop Loss e Modo Escuro"):
    st.markdown("""
    ### 📋 Instruções:
    
    1. **Configurações Básicas**:
       - Defina o **valor inicial** da sua banca
       - Estabeleça uma **meta diária** (%)
       - Configure o **stop loss diário** (% máximo de perda permitido)
    
    2. **Adicionar/Editar Lucros**:
       - Selecione o dia desejado
       - Digite o valor do lucro (use negativo para prejuízo)
       - O sistema alertará se o prejuízo exceder o stop loss
    
    3. **Modo Escuro**:
       - Ative/desative pelo toggle na sidebar
       - Visualização otimizada para ambientes com pouca luz
    
    ### ⚠️ Funcionalidade Stop Loss:
    - O sistema **bloqueia prejuízos acima do limite** configurado
    - Uma **linha tracejada vermelha** no gráfico mostra o limite diário
    - **Alertas visuais** indicam violações do stop loss
    
    ### 🎨 Modo Escuro:
    - Interface escura para reduzir fadiga visual
    - Cores adaptadas para melhor contraste
    - Ideal para uso noturno ou em ambientes escuros
    """)

# Estatísticas adicionais
with st.expander("📊 Estatísticas Detalhadas"):
    days_with_profit = sum(1 for p in st.session_state.daily_profits if p is not None and p > 0)
    days_with_loss = sum(1 for p in st.session_state.daily_profits if p is not None and p < 0)
    days_pending = sum(1 for p in st.session_state.daily_profits if p is None)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dias com Lucro", days_with_profit)
    with col2:
        st.metric("Dias com Prejuízo", days_with_loss)
    with col3:
        st.metric("Dias Pendentes", days_pending)


