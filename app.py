import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

SUPABASE_URL = "https://adpemiisstnvleofyagi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkcGVtaWlzc3Rudmxlb2Z5YWdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MzAyMTgsImV4cCI6MjA3MzEwNjIxOH0.blHm9ufS3fQUXvwj2CBDtPqzVhYeP8HZ83wXrnkuoFM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def carregar_lucros():
    try:
        response = supabase.table("lucros_diarios").select("*").order("dia").execute()
        return {item["dia"]: item["lucro"] for item in response.data}
    except Exception as e:
        st.warning(f"Erro ao carregar dados do Supabase: {e}. Usando dados locais.")
        return {}

def salvar_lucro(dia, lucro):
    try:
        # Se o lucro for None, remover do banco, caso contrário, upsert
        if lucro is None:
            supabase.table("lucros_diarios").delete().eq("dia", dia).execute()
            st.success(f"✅ Lucro do dia {dia} removido do banco de dados!")
        else:
            supabase.table("lucros_diarios").upsert({"dia": dia, "lucro": float(lucro)}).execute()
            st.success(f"✅ Lucro do dia {dia} salvo no banco de dados!")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar no Supabase: {e}")
        return False

def limpar_todos_dados():
    try:
        # Limpar todos os registros da tabela
        supabase.table("lucros_diarios").delete().neq("dia", 0).execute()
        st.success("✅ Todos os dados foram removidos do banco de dados!")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao limpar dados do Supabase: {e}")
        return False

# Carregar dados do Supabase ao iniciar
if 'daily_profits' not in st.session_state:
    lucros = carregar_lucros()
    st.session_state.daily_profits = [lucros.get(i+1, None) for i in range(30)]

# Configuração da página
st.set_page_config(
    page_title="Gestão de Capital",
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
    st.session_state.stop_loss = 5.00
    
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
    
if 'editing_day' not in st.session_state:
    st.session_state.editing_day = None

# Variável para controle de edição rápida
if 'quick_edit_day' not in st.session_state:
    st.session_state.quick_edit_day = None

# Aplicar modo escuro se ativado
if st.session_state.dark_mode:
    dark_mode_css = """
    <style>
    :root {
        --primary-bg: #0f172a;
        --secondary-bg: #1e293b;
        --tertiary-bg: #334155;
        --primary-text: #f1f5f9;
        --secondary-text: #cbd5e1;
        --border-color: #475569;
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    .stApp {
        background-color: var(--primary-bg);
        color: var(--primary-text);
    }
    
    /* Sidebar e elementos principais */
    .css-18e3th9, .css-1d391kg, .st-bb, .st-at, .st-bh, .st-bx {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-text) !important;
    }
    
    /* Inputs */
    .stNumberInput input, .stTextInput input, .stSelectbox select {
        background-color: var(--tertiary-bg) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
    }
    
    /* Labels dos inputs */
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: var(--secondary-text) !important;
        font-weight: 500 !important;
    }
    
    /* Tabelas */
    .stDataFrame {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-text) !important;
    }
    
    /* Métricas */
    .stMetric {
        background-color: var(--secondary-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    .stMetric label {
        color: var(--secondary-text) !important;
        font-size: 0.9rem !important;
    }
    
    .stMetric div {
        color: var(--primary-text) !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
    }
    
    /* Botões */
    .stButton button {
        background-color: var(--accent-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background-color: #2563eb !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Tabs e seções */
    .css-1y4v5go {
        background-color: var(--secondary-bg) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--secondary-bg) !important;
        border-bottom: 1px solid var(--border-color) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--secondary-text) !important;
        padding: 10px 16px !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-color) !important;
        border-bottom: 2px solid var(--accent-color) !important;
    }
    
    /* Alertas personalizados */
    .stop-loss-warning {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%) !important;
        color: white !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .stop-loss-safe {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%) !important;
        color: white !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .stop-loss-info {
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%) !important;
        color: white !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-text) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background-color: var(--secondary-bg) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Checkbox */
    .stCheckbox [data-baseweb="checkbox"] {
        background-color: var(--tertiary-bg) !important;
        border-color: var(--border-color) !important;
    }
    
    .stCheckbox label {
        color: var(--primary-text) !important;
    }
    
    /* Divider */
    hr {
        border-color: var(--border-color) !important;
        margin: 20px 0 !important;
    }
    
    /* Toggle */
    .stToggle [data-baseweb="toggle"] {
        background-color: var(--tertiary-bg) !important;
    }
    
    .stToggle [data-baseweb="toggle"][aria-checked="true"] {
        background-color: var(--accent-color) !important;
    }
    
    /* Placeholder texto mais claro */
    ::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--tertiary-bg);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-color);
    }
    </style>
    """
    st.markdown(dark_mode_css, unsafe_allow_html=True)
else:
    light_mode_css = """
    <style>
    .stop-loss-warning {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%) !important;
        color: #7f1d1d !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid #ef4444;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stop-loss-safe {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%) !important;
        color: #065f46 !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stop-loss-info {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
        color: #1e3a8a !important;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Scrollbar para modo claro */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    </style>
    """
    st.markdown(light_mode_css, unsafe_allow_html=True)

# Título da aplicação com estilo melhorado
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>
    💰 Gestão de Banca
    </h1>
""", unsafe_allow_html=True)

# Processar edição rápida se houver
if st.session_state.quick_edit_day is not None:
    st.session_state.profit_day_input = st.session_state.quick_edit_day
    st.session_state.daily_profit_input = st.session_state.daily_profits[st.session_state.quick_edit_day - 1] if st.session_state.daily_profits[st.session_state.quick_edit_day - 1] is not None else 0.0
    st.session_state.quick_edit_day = None
    st.rerun()

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Toggle para modo escuro com estilo melhorado
    dark_mode = st.toggle("🌙 Modo Escuro", value=st.session_state.dark_mode, key="dark_mode_toggle")
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.subheader("📊 Parâmetros da Banca")
    
    # CORREÇÃO: Usar float para todos os valores numéricos
    initial_value = st.number_input(
        "Valor Inicial (R$)", 
        min_value=0.0, 
        step=0.01, 
        value=float(st.session_state.initial_value),
        key="initial_value_input"
    )
    
    daily_goal = st.number_input(
        "Meta Diária (%)", 
        min_value=0.0, 
        step=0.01, 
        value=float(st.session_state.daily_goal),
        key="daily_goal_input"
    )
    
    stop_loss = st.number_input(
        "Stop Loss Diário (%)", 
        min_value=0.0, 
        max_value=100.0,
        step=0.01, 
        value=float(st.session_state.stop_loss),
        key="stop_loss_input",
        help="Percentual máximo de perda permitido por dia"
    )
    
    if st.button("🔄 Atualizar Configurações", type="primary"):
        st.session_state.initial_value = initial_value
        st.session_state.daily_goal = daily_goal
        st.session_state.stop_loss = stop_loss
        st.rerun()
    
    st.divider()
    
    st.header("💸 Adicionar/Editar Lucro")
    
    profit_day = st.number_input(
        "Dia", 
        min_value=1, 
        max_value=30, 
        value=st.session_state.get('profit_day_input', 1),
        key="profit_day_input"
    )
    
    # Mostrar valor atual se já existir
    current_profit = st.session_state.daily_profits[profit_day-1]
    profit_value = current_profit if current_profit is not None else 0.0
    
    daily_profit = st.number_input(
        "Lucro do Dia (R$)", 
        step=0.01,
        value=float(profit_value),
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
    
    st.markdown(f'<div class="stop-loss-info">💰 Valor da banca no dia {profit_day}: R$ {current_value_at_day:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stop-loss-info">🛑 Stop Loss máximo: R$ {abs(stop_loss_value):.2f} ({stop_loss}%)</div>', unsafe_allow_html=True)
    
    # Verificar se o prejuízo excede o stop loss (apenas para exibição, não para bloquear)
    if daily_profit < 0 and abs(daily_profit) > stop_loss_value:
        st.markdown(f'<div class="stop-loss-warning">⚠️ ATENÇÃO: Este prejuízo excede o stop loss! Máximo permitido: R$ {abs(stop_loss_value):.2f}</div>', unsafe_allow_html=True)
        allow_save = st.checkbox("💾 Salvar mesmo excedendo o stop loss", value=False)
    else:
        allow_save = True
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar", type="primary", disabled=not allow_save):
            st.session_state.daily_profits[profit_day-1] = daily_profit
            # Salvar no banco de dados
            if salvar_lucro(profit_day, daily_profit):
                st.session_state.editing_day = None
                st.rerun()
    with col2:
        if st.button("🗑️ Limpar", type="secondary"):
            st.session_state.daily_profits[profit_day-1] = None
            # Remover do banco de dados
            if salvar_lucro(profit_day, None):
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

# Exibir métricas com estilo melhorado
st.subheader("📈 Métricas de Desempenho")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Valor Inicial", f"R$ {st.session_state.initial_value:.2f}")
with col2:
    st.metric("📊 Valor Atual", f"R$ {daily_values[-1]:.2f}")
with col3:
    profit_color = "#ef4444" if total_profit < 0 else "#10b981"
    st.metric("💵 Lucro Líquido", f"R$ {total_profit:.2f}", f"{total_percent:.2f}%")
with col4:
    st.metric("🛑 Stop Loss", f"{st.session_state.stop_loss}%")

# Gráfico de evolução
st.subheader("📊 Evolução da Banca")
fig = go.Figure()

# Linha principal da evolução
fig.add_trace(go.Scatter(
    x=list(range(31)),
    y=daily_values,
    mode='lines+markers',
    name='Valor da Banca',
    line=dict(color='#3b82f6', width=3),
    marker=dict(size=6, color='#3b82f6')
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
    line=dict(color='#ef4444', width=2, dash='dash'),
    opacity=0.7
))

# Configuração do layout do gráfico
graph_bgcolor = 'rgba(0,0,0,0)' if st.session_state.dark_mode else 'rgba(255,255,255,1)'
grid_color = '#334155' if st.session_state.dark_mode else '#e2e8f0'
text_color = '#f1f5f9' if st.session_state.dark_mode else '#1e293b'

fig.update_layout(
    xaxis_title="Dia",
    yaxis_title="Valor (R$)",
    hovermode="x unified",
    height=400,
    plot_bgcolor=graph_bgcolor,
    paper_bgcolor=graph_bgcolor,
    font=dict(color=text_color),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color=text_color)
    ),
    xaxis=dict(
        gridcolor=grid_color,
        zerolinecolor=grid_color
    ),
    yaxis=dict(
        gridcolor=grid_color,
        zerolinecolor=grid_color
    )
)

st.plotly_chart(fig, use_container_width=True)

# Tabela de resultados com opção de edição
st.subheader("📋 Controle Diário - 30 Dias")

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
        "Status": "❌ Violado" if (profit is not None and profit < 0) or stop_loss_violated else "✅ Respeitado" if profit is not None else "⏳ Pendente"
    })

# Criar DataFrame
df = pd.DataFrame(table_data)

# Função segura para extrair valores numéricos
def safe_extract_value(cell_value):
    if cell_value == "R$ -":
        return None
    try:
        # Remove "R$ " e converte para float
        return float(cell_value.replace("R$ ", "").strip())
    except (ValueError, AttributeError):
        return None

# CORREÇÃO: Usar Styler.map em vez de Styler.applymap (depreciado)
styled_df = df.style

# Aplicar estilos usando .map (nova versão)
def color_lucro_dia(val):
    if val == "R$ -":
        return 'color: #ef4444; font-weight: bold;'
    elif val.startswith('R$'):
        num_val = safe_extract_value(val)
        if num_val is not None:
            if num_val > 0:
                return 'color: #10b981; font-weight: bold;'
            elif num_val < 0:
                return 'color: #ef4444; font-weight: bold;'
    return ''

def color_percent(val):
    if val.endswith('%') and val != "0.00%":
        num_val = safe_extract_value(val.replace('%', ''))
        if num_val is not None:
            if num_val > 0:
                return 'color: #10b981; font-weight: bold;'
            elif num_val < 0:
                return 'color: #ef4444; font-weight: bold;'
    return ''

def color_status(val):
    if val == '❌ Violado':
        return 'color: #ef4444; font-weight: bold;'
    elif val == '✅ Respeitado':
        return 'color: #10b981; font-weight: bold;'
    return ''

# Aplicar os estilos
styled_df = styled_df.map(color_lucro_dia, subset=['Lucro do Dia'])\
                     .map(color_percent, subset=['% da Banca'])\
                     .map(color_status, subset=['Status'])

# CORREÇÃO: Usar width em vez de use_container_width (depreciado)
st.dataframe(styled_df, width='stretch', hide_index=True)

# Botões de edição rápida
st.subheader("⚡ Edição Rápida por Dia")

# Usar form para evitar o erro de session_state
with st.form("quick_edit_form"):
    cols = st.columns(6)
    for i in range(30):
        with cols[i % 6]:
            day = i + 1
            profit = st.session_state.daily_profits[i]
            button_label = f"Dia {day}" + (f": {profit:.2f}" if profit is not None else "")
            
            # CORREÇÃO: Usar type em vez de use_container_width
            if st.form_submit_button(button_label, type="primary"):
                st.session_state.quick_edit_day = day
                st.rerun()

# Botão para resetar todos os dados
if st.button("🔄 Resetar Todos os Dados", type="secondary"):
    # Limpar dados da sessão
    for key in st.session_state.keys():
        if key not in ['dark_mode', 'stop_loss']:
            del st.session_state[key]
    
    # Limpar dados do banco de dados
    if limpar_todos_dados():
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
       - O sistema alertará se o prejuízo exceder o stop loss, mas permitirá salvar
    
    3. **Modo Escuro**:
       - Ative/desative pelo toggle na sidebar
       - Visualização otimizada para ambientes com pouca luz
    
    ### ⚠️ Funcionalidade Stop Loss:
    - O sistema **alerta sobre prejuízos acima do limite** configurado
    - Uma **linha tracejada vermelha** no gráfico mostra o limite diário
    - **Alertas visuais** indicam violações do stop loss
    - **Não bloqueia** a inserção de valores, apenas alerta
    
    ### 🎨 Modo Escuro Elegante:
    - Interface escura com gradientes sofisticados
    - Cores harmoniosas e contrastes perfeitos
    - Design moderno e minimalista
    - Ideal para uso prolongado sem fadiga visual
    """)

# Estatísticas adicionais
with st.expander("📊 Estatísticas Detalhadas"):
    days_with_profit = sum(1 for p in st.session_state.daily_profits if p is not None and p > 0)
    days_with_loss = sum(1 for p in st.session_state.daily_profits if p is not None and p < 0)
    days_pending = sum(1 for p in st.session_state.daily_profits if p is None)
    days_stop_loss_violated = sum(1 for i, p in enumerate(st.session_state.daily_profits) 
                               if p is not None and p < 0 and 
                               abs(p) > (st.session_state.initial_value * (st.session_state.stop_loss / 100)))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📈 Dias com Lucro", days_with_profit)
    with col2:
        st.metric("📉 Dias com Prejuízo", days_with_loss)
    with col3:
        st.metric("⏰ Dias Pendentes", days_pending)
    with col4:
        st.metric("🛑 Stop Loss Violado", days_stop_loss_violated)

# Seção de debug para verificar conexão com o banco
with st.expander("🔧 Debug - Status do Banco de Dados"):
    try:
        # Testar conexão
        response = supabase.table("lucros_diarios").select("count", count="exact").execute()
        st.success(f"✅ Conexão com Supabase bem-sucedida!")
        st.info(f"📊 Total de registros na tabela: {response.count}")
        
        # Mostrar alguns registros
        records = supabase.table("lucros_diarios").select("*").order("dia").limit(5).execute()
        if records.data:
            st.write("📝 Últimos registros:")
            for record in records.data:
                st.write(f"- Dia {record['dia']}: R$ {record['lucro']:.2f}")
        else:
            st.info("ℹ️ Nenhum registro encontrado na tabela.")
            
    except Exception as e:
        st.error(f"❌ Erro ao conectar com o banco: {e}")

