import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import altair as alt
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA E TEMA
# ---------------------------------------------------------
st.set_page_config(page_title="Super Connect | Retenção", layout="wide", page_icon="📉", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    /* ==========================================
    
    /* Garante que o texto digitado e selecionado ficará visível e branco */
    div[data-baseweb="input"] input, 
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }
       REMOVER LIMITADORES DO MENU (CORREÇÃO DEFINITIVA 3.0)
       ========================================== */
    /* 1. MATA O SVG DE TELA CHEIA: Como o seu menu roda dentro de um iframe seguro, ocultar os SVGs da barra lateral apaga os cantinhos nativos sem afetar os ícones do seu menu! */
    section[data-testid="stSidebar"] div[data-testid="stElementContainer"] svg {
        display: none !important;
    }
    
    /* 2. Oculta a barra de ferramentas invisível do Streamlit e botões de tela cheia */
    section[data-testid="stSidebar"] div[data-testid="stElementToolbar"],
    section[data-testid="stSidebar"] button[title="View fullscreen"] {
        display: none !important;
    }
    
    /* 3. Limpa completamente bordas e focos do contêiner e do iframe */
    section[data-testid="stSidebar"] iframe,
    section[data-testid="stSidebar"] div[data-testid="stCustomComponentV1"],
    section[data-testid="stSidebar"] div[data-testid="stCustomComponentV1"] > div {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }
    /* ========================================== */
    
    /* 1. Campos de Texto e Resumo */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stTextArea"] textarea {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    
    /* 2. FORÇA O FUNDO CLARO NAS CAIXAS MESTRAS (Corrige o fundo preto da Tela 1) */
div[data-testid="stSelectbox"], 
div[data-testid="stMultiSelect"] {
    --secondary-background-color: #f8fafc !important;
    --text-color: #0f172a !important;
}
div[data-testid="stSelectbox"] > div > div, 
div[data-testid="stMultiSelect"] > div > div {
    background-color: #f8fafc !important;
}

/* 3. BORDAS E FUNDO INTERNO DA CAIXA */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div, 
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div { 
    background-color: transparent !important; 
    border: 1px solid #cbd5e1 !important; 
    border-radius: 6px !important;
}

/* 4. TEXTO ESCURO NO SELECTBOX (Seguro usar o asterisco aqui pois não tem chips) */
div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: #0f172a !important;
    fill: #0f172a !important;
}

/* 5. TEXTO ESCURO NO MULTISELECT (Atinge só o texto solto e setas, poupando os chips) */
div[data-testid="stMultiSelect"] div[data-baseweb="select"] input,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div > div > div,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] svg {
    color: #0f172a !important;
    fill: #0f172a !important;
}

/* 6. CHIPS DO MULTISELECT: Fundo Verde Esmeralda e Letras Brancas */
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #10b981 !important;
    border: none !important;
}
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    background-color: transparent !important;
}

/* 7. MÁGICA DO DROPDOWN: Lista flutuante clara */
div[data-baseweb="popover"] > div, 
ul[data-baseweb="menu"] {
    background-color: #f8fafc !important;
}
ul[data-baseweb="menu"] li, 
ul[data-baseweb="menu"] li span {
    color: #0f172a !important;
    background-color: transparent !important;
}

/* 8. BOTÃO DE "LIMPAR FILTROS" NO MODO CLARO */
div[data-testid="stButton"] button {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}
div[data-testid="stButton"] button p {
    color: #0f172a !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #10b981 !important;
    background-color: #f8fafc !important;
}
div[data-testid="stButton"] button:hover p {
    color: #10b981 !important;
}
/* 9. BORDA MAIS ESCURA NO CAMPO DE PERÍODO (DATA) */
div[data-testid="stDateInput"] div[data-baseweb="input"] {
    border: 1px solid #94a3b8 !important; 
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INICIALIZAÇÃO DO BANCO DE DADOS (SUPABASE NA NUVEM)
# ---------------------------------------------------------
# 1. Conecta com segurança usando os segredos do arquivo .toml
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Funções inteligentes para puxar e traduzir os dados da nuvem
@st.cache_data(ttl=5) 
def carregar_usuarios():
    resposta = supabase.table("usuarios").select("*").execute()
    # Se o banco devolver vazio, força a criação das colunas para não dar erro
    if not resposta.data:
        return pd.DataFrame(columns=["ID", "Nome", "Email", "Senha", "Funcao"])
    
    df = pd.DataFrame(resposta.data)
    # Traduz as colunas que vieram do banco para o padrão maiúsculo
    return df.rename(columns={"id": "ID", "nome": "Nome", "email": "Email", "senha": "Senha", "funcao": "Funcao"})

@st.cache_data(ttl=5)
def carregar_colaboradores():
    resposta = supabase.table("colaboradores").select("*").execute()
    # Se o banco devolver vazio, força a criação das colunas
    if not resposta.data:
        return pd.DataFrame(columns=["ID", "Nome", "Cargo", "Status"])
    
    df = pd.DataFrame(resposta.data)
    return df.rename(columns={"id": "ID", "nome": "Nome", "cargo": "Cargo", "status": "Status"})

@st.cache_data(ttl=5)
def carregar_atendimentos():
    resposta = supabase.table("atendimentos").select("*").execute()
    # Se o banco estiver vazio, cria uma tabela com as colunas certas com letras maiúsculas
    if not resposta.data:
        return pd.DataFrame(columns=["Data", "Cliente", "ID", "Cidade", "Plano Cancelado", 
                                     "Valor Perdido", "Status", "Motivo", "Detalhes", "Colaborador"])
    
    df = pd.DataFrame(resposta.data)
    # Traduz as colunas do banco para o padrão visual do seu sistema
    df = df.rename(columns={
        "data": "Data", "cliente": "Cliente", "id_cliente": "ID", "cidade": "Cidade", 
        "plano_cancelado": "Plano Cancelado", "valor_perdido": "Valor Perdido", 
        "status": "Status", "motivo": "Motivo", "detalhes": "Detalhes", "colaborador": "Colaborador"
    })
    return df

# 3. Carrega os dados reais para a sessão atual
st.session_state.usuarios = carregar_usuarios()
st.session_state.colaboradores = carregar_colaboradores()
st.session_state.atendimentos = carregar_atendimentos()

# Controle de sessão (quem está logado) - Mantido igual
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usuario_logado = None

# Lista fixa de motivos - Mantido igual
MOTIVOS = [
    "Insatisfação", 
    "Mudança de endereço", 
    "Inviabilidade", 
    "Problemas financeiros", 
    "Revertido", 
    "Outros"
]

# ---------------------------------------------------------
# TELA DE LOGIN (Barreira de Acesso com Imagem de Fundo)
# ---------------------------------------------------------
if not st.session_state.logged_in:
    import base64

    # 1. Função para carregar a imagem e converter para o CSS
    def get_base64_of_bin_file(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except FileNotFoundError:
            return ""

    # Carrega a imagem PNG
    nome_da_imagem = "Background sistema retenção.png" 
    img_base64 = get_base64_of_bin_file(nome_da_imagem)

    # 2. Injeta o CSS exclusivo da página de Login
    st.markdown(f"""
        <style>
        /* Imagem de fundo cobrindo a tela inteira */
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center top; /* Garante que o topo da imagem fique visível */
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Oculta a barra lateral e o cabeçalho superior na tela de login */
        section[data-testid="stSidebar"] {{ display: none !important; }}
        header[data-testid="stHeader"] {{ background-color: transparent !important; }}

        /* Estiliza o Formulário de Login (Vidro Escuro) */
        div[data-testid="stForm"] {{
            background-color: rgba(15, 23, 42, 0.85) !important; 
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important; 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important; 
            padding: 30px 20px !important;
            margin-top: 200px !important; /* EMPURRA A CAIXA PARA BAIXO, LIBERANDO A LOGO */
        }}
        
        /* Ajusta as cores do texto dos campos para o fundo escuro */
        div[data-testid="stForm"] p, 
        div[data-testid="stForm"] label {{
            color: #f8fafc !important;
        }}
        
        /* --- CORREÇÃO DO BOTÃO ENTRAR --- */
        div[data-testid="stFormSubmitButton"] button {{
            background-color: #1e293b !important; /* Fundo escuro no botão */
            color: #f8fafc !important; /* Letra branca */
            border: 1px solid #475569 !important;
        }}
        div[data-testid="stFormSubmitButton"] button p {{
            color: #f8fafc !important;
        }}
        
        /* Efeito ao passar o mouse no botão (Verde Neon combinando com o fundo) */
        div[data-testid="stFormSubmitButton"] button:hover {{
            border-color: #39ff14 !important; 
            background-color: #0f172a !important;
        }}
        div[data-testid="stFormSubmitButton"] button:hover p {{
            color: #39ff14 !important;
        }}
        
        /* Remove a borda do container vazio */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            border: none !important;
            background: transparent !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # 3. Proporção das colunas: 1.5 (laterais maiores) e 1 (meio menor) para espremer a caixa
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    
    with col2:
        # Textos "ACESSO RESTRITO" removidos completamente!
        
        with st.form("form_login"):
            email_input = st.text_input("E-mail")
            senha_input = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar", use_container_width=True)
            
            if btn_login:
                df_users = st.session_state.usuarios
                user_match = df_users[(df_users["Email"] == email_input) & (df_users["Senha"] == senha_input)]
                
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.usuario_logado = user_match.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")
                    
    # Interrompe o carregamento do resto do site se não logar
    st.stop()
    
# ---------------------------------------------------------
# MENU LATERAL (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
            
            /* 1. Muda o fundo da barra lateral inteira para o verde pastel suave */
            section[data-testid="stSidebar"] {
                background-color: #d1e8db !important;
            }
            
            /* 3. Estilo do Título (agora escuro para dar contraste com o verde) */
            .titulo-sidebar {
                font-family: 'Bebas Neue', sans-serif;
                font-size: 50px;
                text-align: center;
                color: #0f172a; /* Tom bem escuro para leitura perfeita */
                text-transform: uppercase;
                margin-bottom: 5px;
                letter-spacing: 2px;
                line-height: 0.85;
            }
            
            /* 4. Estilo do Subtítulo */
            .subtitulo-sidebar {
                text-align: center;
                color: #475569; /* Cinza médio elegante */
                font-size: 14px;
                margin-bottom: 15px;
                font-weight: 500;
            }

    /* 6. Corrige a cor escura dos campos de Data (Calendário) */
    div[data-testid="stDateInput"] div[data-baseweb="input"] {
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stDateInput"] input {
        color: #0f172a !important;
        background-color: transparent !important;
    }
    
    div[data-testid="stDateInput"] svg {
        fill: #0f172a !important; /* Mantém o ícone do calendário visível */
    }

    /* Remove o espaço em branco gigante no topo da barra lateral */
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {
            padding-top: 1rem !important;
        }

</style>
""", unsafe_allow_html=True) # 1. FECHAMOS A CAIXA DO CSS AQUI

    # 2. INSERIMOS A IMAGEM NO PYTHON (FORA DAS ASPAS)
    st.image("images-Photoroom.png", use_container_width=True)

    # 3. ABRIMOS UMA NOVA CAIXA SÓ PARA O SUBTÍTULO
    st.markdown("""
        <div class="subtitulo-sidebar" style="margin-top: -15px; margin-bottom: 20px; text-align: center;">
            RETENÇÃO E CANCELAMENTO
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    # Lógica que muda as variáveis de cor do menu de acordo com o interruptor
    estado_tema = st.session_state.get("toggle_tema", False)

    # Força uma cor de fundo vibrante para a barra lateral APENAS no Modo Claro
    if not estado_tema:
        st.markdown("""
            <style>
            section[data-testid="stSidebar"] {
                background-color: #10b981 !important; /* Verde Esmeralda Vibrante */
            }
            </style>
        """, unsafe_allow_html=True)

    # Cores dos botões do menu (No modo claro, usamos o mesmo verde do fundo para camuflar)
    cor_fundo_menu = "#1e293b" if estado_tema else "#10b981" # <-- Trocamos "transparent" por "#10b981"
    cor_texto_menu = "#f8fafc" if estado_tema else "#ffffff"
    cor_hover = "rgba(255, 255, 255, 0.05)" if estado_tema else "rgba(255, 255, 255, 0.2)"
    cor_selecionado = "rgba(255, 255, 255, 0.1)" if estado_tema else "rgba(255, 255, 255, 0.35)"

# Descobre a função de quem fez o login
    funcao_atual = st.session_state.usuario_logado["Funcao"]
    
    if funcao_atual == "Supervisor":
        # Supervisor vê tudo
        opcoes_menu = ["Novo Atendimento", "Dashboard", "Colaboradores", "Relatórios"]
        icones_menu = ["headset", "grid", "people", "graph-up-arrow"]
    else:
        # Operador só vê a tela de registro
        opcoes_menu = ["Novo Atendimento", "Dashboard"]
        icones_menu = ["headset", "grid"]

    # Usando o Option Menu dinâmico
    menu = option_menu(
        menu_title=None,  
        options=opcoes_menu,
        icons=icones_menu,  
        default_index=0,
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": cor_fundo_menu, 
                "border": "none",
                "transition": "background-color 0.3s ease"
            },
            "icon": {
                "color": cor_texto_menu, 
                "font-size": "18px",
                "transition": "color 0.3s ease"
            }, 
            "nav-link": {
                "font-family": "'Bebas Neue', sans-serif",
                "font-size": "18px", 
                "text-align": "left", 
                "margin": "8px 0px", 
                "color": cor_texto_menu,
                "--hover-color": cor_hover,
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background-color": cor_selecionado,
                "color": cor_texto_menu
            },
        }
    )
    st.divider()
    # Mostra quem está logado
    st.caption(f"👤 **{st.session_state.usuario_logado['Nome']}** ({funcao_atual})")
    
    # 1. Define as cores do botão Sair dinamicamente (Claro/Escuro)
    cor_fundo_sair = "transparent" if estado_tema else "#ffffff"
    cor_texto_sair = "#f8fafc" if estado_tema else "#0f172a"
    cor_borda_sair = "#475569" if estado_tema else "#94a3b8"

    # 2. Aplica o CSS exclusivo para os botões da barra lateral
    st.markdown(f"""
        <style>
        /* Estiliza o botão de Sair */
        section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
            background-color: {cor_fundo_sair} !important;
            color: {cor_texto_sair} !important;
            border: 1px solid {cor_borda_sair} !important;
            transition: all 0.3s ease;
        }}
        /* Garante que a cor da letra mude junto */
        section[data-testid="stSidebar"] div[data-testid="stButton"] button p {{
            color: {cor_texto_sair} !important;
        }}
        
        /* Efeito ao passar o mouse (Fica vermelho em qualquer tema) */
        section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {{
            border-color: #ef4444 !important;
            background-color: transparent !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover p {{
            color: #ef4444 !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # 3. Botão limpo, sem emoji
    if st.button("Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.usuario_logado = None
        st.rerun()

        # --- NOVO RODAPÉ DA BARRA LATERAL ---
    # Usamos a cor do texto do menu para garantir que fique legível tanto no claro quanto no escuro
    st.markdown(f"""
        <div style="text-align: center; margin-top: 30px; font-size: 12px; color: {cor_texto_menu}; opacity: 0.7;">
            v1.0 • Setor de Retenção
        </div>
    """, unsafe_allow_html=True)

   # ---------------------------------------------------------
# INTERRUPTOR DE TEMA (Canto superior direito)
# ---------------------------------------------------------
# Lê o estado atual do interruptor para mudar o texto e o emoji dinamicamente
estado_tema = st.session_state.get("toggle_tema", False)
label_tema = "☀️ Modo Claro" if estado_tema else "🌙 Modo Escuro"
tema_escuro = st.toggle(label_tema, key="toggle_tema")

# Injeta o CSS para fixar o botão no topo absoluto à direita
st.markdown("""
    <style>
    div[data-testid="stElementContainer"]:has(input[type="checkbox"]) {
        position: fixed !important;
        top: 70px !important;
        right: 25px !important;
        width: auto !important;
        z-index: 9999999 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Se o interruptor estiver ligado, injeta o CSS do Modo Escuro corrigido por cima
if tema_escuro:
    st.markdown("""
        <style>
        /* Fundo geral e cor de texto base */
        .stApp {
            background-color: #0f172a !important; 
        }
        
        /* Pinta a barra nativa do Streamlit com a cor do Modo Escuro */
    header[data-testid="stHeader"] {
        background-color: #0f172a !important;
    }
        
        /* Força todos os textos comuns a ficarem claros */
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp div[data-testid="stMetricValue"] {
            color: #f8fafc !important; 
        }
        
        /* Fundo da barra lateral */
        section[data-testid="stSidebar"] {
            background-color: #1e293b !important; 
        }
        
        /* Títulos da barra lateral */
        .titulo-sidebar {
            color: #d1e8db !important; 
        }
        .subtitulo-sidebar {
            color: #94a3b8 !important; 
        }
        
        /* Campos de Texto e Data */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stDateInput"] div[data-baseweb="input"] {
            background-color: #334155 !important; 
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important; /* Força a cor da fonte internamente */
            border: 1px solid #475569 !important;
        }
        
        /* Caixas de Seleção e Múltipla */
        div[data-testid="stSelectbox"], div[data-testid="stMultiSelect"] {
        --secondary-background-color: #334155 !important;
        --text-color: #f8fafc !important;
        }
        div[data-testid="stSelectbox"] > div > div, div[data-testid="stMultiSelect"] > div > div {
        background-color: #334155 !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div, div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background-color: transparent !important;
        border: 1px solid #475569 !important;
        }
        div[data-testid="stSelectbox"] *, div[data-testid="stMultiSelect"] * {
        color: #f8fafc !important;
        }

        /* Colore os ícones dos campos e a setinha do cabeçalho de branco no Modo Escuro */ 
        div[data-testid="stDateInput"] svg, 
        div[data-testid="stSelectbox"] svg,
        div[data-testid="stMultiSelect"] svg,
        header[data-testid="stHeader"] svg {
        fill: #f8fafc !important;
        color: #f8fafc !important;
        }
        
        /* --- CORREÇÃO DOS BOTÕES DE FORMULÁRIO --- */
        div[data-testid="stFormSubmitButton"] button, 
        div[data-testid="stButton"] button,
        button[data-baseweb="button"] {
            background-color: #334155 !important;
            color: #f8fafc !important;
            border: 1px solid #475569 !important;
        }
        
        /* Força a cor da fonte dentro do botão */
        div[data-testid="stFormSubmitButton"] button p, 
        div[data-testid="stButton"] button p {
            color: #f8fafc !important;
        }
        
        /* Efeito ao passar o mouse nos botões */
        div[data-testid="stFormSubmitButton"] button:hover, 
        div[data-testid="stButton"] button:hover,
        button[data-baseweb="button"]:hover {
            border-color: #d1e8db !important;
            background-color: #1e293b !important;
        }
        
        div[data-testid="stFormSubmitButton"] button:hover p, 
        div[data-testid="stButton"] button:hover p {
            color: #d1e8db !important;
        }
        
        /* Colore os ícones dos campos e a setinha do cabeçalho de branco no Modo Escuro */
        div[data-testid="stDateInput"] svg, 
        div[data-testid="stSelectbox"] svg,
        header[data-testid="stHeader"] svg {
            fill: #f8fafc !important;
            color: #f8fafc !important;
        }
        </style>
    """, unsafe_allow_html=True)
st.write("")
st.write("")

# --- MÁGICA DO TEMA NAS TABELAS ---
# Função que escurece as tabelas se o interruptor estiver ligado
def aplicar_tema_tabela(df_alvo):
    if estado_tema:
        return df_alvo.style.set_properties(**{
            'background-color': '#1e293b',
            'color': '#f8fafc',
            'border-color': '#475569'
        }).set_table_styles([
            # Força o fundo escuro especificamente nos cabeçalhos (Topo)
            {'selector': 'thead th', 'props': [
                ('background-color', '#334155 !important'), 
                ('color', '#f8fafc !important'),
                ('border', '1px solid #475569 !important')
            ]},
            # Pega qualquer outro elemento de cabeçalho residual
            {'selector': 'th', 'props': [
                ('background-color', '#334155 !important'), 
                ('color', '#f8fafc !important')
            ]}
        ])
    return df_alvo

# ---------------------------------------------------------
# TELA 1: NOVO ATENDIMENTO (Baseado na image_ef1e57.png)
# ---------------------------------------------------------
if menu == "Novo Atendimento":
    st.header("Registrar Atendimento")
    st.caption("Preencha os dados após cada ligação. A data e hora são registradas automaticamente.")
    
    with st.container(border=True):
        with st.form("form_registro", clear_on_submit=True):
                # Alteramos de 2 para 3 colunas no topo
            col1, col2, col3 = st.columns(3)
            with col1:
                cliente = st.text_input("Nome do Cliente *", placeholder="Ex.: João da Silva")
            with col2:
                id_cliente = st.text_input("ID do Cliente *", placeholder="Ex.: 10243578")
            with col3:
                cidade = st.text_input("Cidade *", placeholder="Ex.: Nome da cidade")

            # --- NOVOS CAMPOS FINANCEIROS E DE PLANO ---
            col_plano, col_valor, col_status = st.columns(3)
            with col_plano:
                lista_planos = [
                    "Selecione o plano...", "Internet", "Câmera", "Chip", "TV", 
                    "Internet+Câmera", "Internet+Chip", "Internet+TV", 
                    "Câmera+Chip", "Câmera+TV", "Chip+TV", "Internet+Câmera+Chip", 
                    "Internet+Câmera+TV", "Internet+Chip+TV", "Câmera+Chip+TV", 
                    "Internet+Câmera+Chip+TV"
                ]
                plano_cancelado = st.selectbox("Plano Alvo do Cancelamento *", lista_planos)
                
            with col_valor:
                valor_perdido = st.text_input("Valor em Risco/Perdido (R$) *", placeholder="Ex.: 150,50")
                
            with col_status:
                status_retencao = st.selectbox("Status Final da Retenção *", ["Selecione...", "Cancelamento Concluído", "Cliente Retido/Revertido"])

            # --- MOTIVOS E MIGRAÇÃO ---
            col_motivo, col_migrado = st.columns(2)
            with col_motivo:
                # Substitua 'MOTIVOS' abaixo pela variável ou lista exata que estava no final da sua linha 546
                motivo = st.selectbox("Motivo Principal *", ["Selecione o motivo principal..."] + MOTIVOS)
            
            with col_migrado:
                lista_migrados = ["Não se aplica (Cancelado)"] + lista_planos[1:]
                plano_migrado = st.selectbox("Plano Migrado (Em caso de Retenção)", lista_migrados)

            # --- COLABORADOR E RESUMO (MANTIDO O SEU ORIGINAL) ---
                # 1. Pegamos a tabela e transformamos a primeira coluna (os nomes) em uma lista normal
            try:
                # Tenta buscar pela coluna 'Nome' se for um DataFrame
                nomes = st.session_state.colaboradores['Nome'].tolist()
            except:
                # Se for uma Series ou lista, converte direto
                nomes = list(st.session_state.colaboradores)
                
            # 2. Agora sim juntamos os textos perfeitamente!
            lista_colaboradores = ["Selecione o colaborador..."] + nomes
            colaborador = st.selectbox("Colaborador Responsável *", lista_colaboradores)

            detalhes = st.text_area("Motivo Detalhado (Resumo)", placeholder="Resumo da ligação...")
            
            col_submit, col_clear = st.columns([8, 1])
            with col_submit:
                submit = st.form_submit_button("Registrar Atendimento", use_container_width=True)
            with col_clear:
                st.form_submit_button("Limpar", use_container_width=True)
            # --- LÓGICA DE ENVIO PARA O SUPABASE ---
            if submit:
                # 1. Trava de segurança: Verifica se os campos com (*) foram preenchidos
                if not cliente or not id_cliente or not cidade or plano_cancelado == "Selecione o plano..." or valor_perdido == "" or status_retencao == "Selecione..." or motivo == "Selecione o motivo principal..." or colaborador == "Selecione o colaborador...":
                    st.error("⚠️ Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    # 2. Transforma o valor digitado (ex: "150,50") em um número que o banco entende ("150.50")
                    try:
                        valor_formatado = float(valor_perdido.replace(".", "").replace(",", "."))
                    except ValueError:
                        st.error("⚠️ Digite um valor válido no formato 150,50")
                        st.stop()
                    
                    # Puxa a data e hora exata do clique
                    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    # 3. Prepara o pacote de dados EXATAMENTE como o banco de dados espera (letras minúsculas)
                    dados_para_nuvem = {
                        "data": data_atual,
                        "cliente": cliente,
                        "id_cliente": id_cliente,
                        "cidade": cidade,
                        "plano_cancelado": plano_cancelado,
                        "valor_perdido": valor_formatado,
                        "status": status_retencao,
                        "motivo": motivo,
                        "detalhes": detalhes,
                        "colaborador": colaborador
                    }
                    
                    # 4. Manda o Supabase inserir e atualiza as memórias
                    try:
                        supabase.table("atendimentos").insert(dados_para_nuvem).execute()
                        
                        # 1º Passo: Limpa o cache antigo do servidor
                        st.cache_data.clear() 
                        
                        # 2º Passo: Força o sistema a buscar a tabela nova imediatamente!
                        st.session_state.atendimentos = carregar_atendimentos()
                        
                        st.success("✅ Atendimento registrado e salvo na nuvem com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar na nuvem: {e}")

        if submit:
            # 1. A NOVA TRAVA DE SEGURANÇA (Agora exige plano e status também)
            if (not cliente or not id_cliente or not cidade.strip() or not detalhes.strip() or 
                motivo.startswith("Selecione") or colaborador.startswith("Selecione") or 
                plano_cancelado.startswith("Selecione") or status_retencao.startswith("Selecione")):
                
                st.warning("⚠️ Por favor, preencha todos os campos obrigatórios antes de submeter o atendimento.")
            
            else:
                # 2. CÁLCULO DA PERDA FINANCEIRA
                # Transforma o texto (ex: "150,50") em número matemático (ex: 150.50)
                try:
                    valor_num = float(valor_perdido.replace(",", ".")) if valor_perdido else 0.0
                except ValueError:
                    valor_num = 0.0 
                
                perda_real = valor_num if status_retencao == "Cancelamento Concluído" else 0.0

                # 3. PREPARANDO O PACOTE DE DADOS COM AS NOVAS VARIÁVEIS
                novo_dado = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Cliente": cliente, 
                    "ID": id_cliente, 
                    "Cidade": cidade.title(),
                    "Plano Cancelado": plano_cancelado, 
                    "Valor Perdido": perda_real,
                    "Status": status_retencao, 
                    "Motivo": motivo, 
                    "Detalhes": detalhes, 
                    "Colaborador": colaborador
                }
                
                # 4. SALVANDO NO BANCO DE DADOS DA SESSÃO
                novo_df = pd.DataFrame([novo_dado])
                st.session_state.atendimentos = pd.concat([st.session_state.atendimentos, novo_df], ignore_index=True)
                
                st.success("Atendimento registrado com sucesso!")
                    
# ---------------------------------------------------------
# TELA 2: DASHBOARD
# ---------------------------------------------------------
elif menu == "Dashboard":

    # Organizando os filtros no topo
    col_titulo, col_de, col_ate, col_colab = st.columns([3, 1, 1, 1])
    
    with col_titulo:
        st.header("Dashboard da Supervisão")
        st.caption("Métricas em tempo real da retenção e cancelamento.")
        
    with col_de:
        data_inicio = st.date_input("De:", format="DD/MM/YYYY")
        
    with col_ate:
        data_fim = st.date_input("Até:", format="DD/MM/YYYY")
        
    with col_colab:
        opcoes_colaboradores = ["Todos"] + st.session_state.colaboradores["Nome"].tolist()
        filtro_colab = st.selectbox("Colaborador", opcoes_colaboradores)
    
    # Faz uma cópia do banco de dados para não apagar os dados originais ao filtrar
    df = st.session_state.atendimentos.copy()
    
    if not df.empty:
        df["Data_Calculo"] = pd.to_datetime(df["Data"], format="%d/%m/%Y %H:%M").dt.date
        df = df[(df["Data_Calculo"] >= data_inicio) & (df["Data_Calculo"] <= data_fim)]
        
        if filtro_colab != "Todos":
            df = df[df["Colaborador"] == filtro_colab]
    
    # Cálculos das métricas 
    total_atendimentos = len(df)
    retidos = len(df[df["Motivo"] == "Revertido"]) if not df.empty else 0
    cancelados = total_atendimentos - retidos
    taxa_retencao = f"{(retidos / total_atendimentos * 100):.1f}%" if total_atendimentos > 0 else "0.0%"

    # Linha de Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("TOTAL DE ATENDIMENTOS", total_atendimentos)
    with col2:
        st.metric("CANCELADOS", cancelados)
    with col3:
        st.metric("RETIDOS (REVERTIDO)", retidos)
    with col4:
        st.metric("TAXA DE RETENÇÃO", taxa_retencao)
    
    st.divider()

    # Linha de Gráficos e Resumo
    col_grafico, col_resumo = st.columns([2, 1])
    
    with col_grafico:
        st.subheader("Cancelamentos por Motivo Principal")
        st.caption("Distribuição dos maiores ofensores no período selecionado.")
        
        if not df.empty:
            dados_grafico = df["Motivo"].value_counts().reset_index()
            dados_grafico.columns = ["Motivo", "Quantidade"]
            
            # --- MÁGICA DO TEMA NO GRÁFICO ---
            # Configuração das cores baseada no interruptor
            cor_fundo = "#0f172a" if estado_tema else "transparent"
            cor_texto = "#f8fafc" if estado_tema else "#0f172a"
            cor_linha = "#334155" if estado_tema else "#e2e8f0"
            
            grafico = alt.Chart(dados_grafico).mark_bar(
                size=35,
                cornerRadiusTopLeft=6,
                cornerRadiusTopRight=6
            ).encode(
                x=alt.X('Motivo', sort='-y', title=None, axis=alt.Axis(labelAngle=-40)),
                y=alt.Y('Quantidade', title=None),
                color=alt.Color('Motivo', legend=None, scale=alt.Scale(scheme='set2')),
                tooltip=['Motivo', 'Quantidade']
            ).properties(
                height=350
            ).configure(
                background=cor_fundo
            ).configure_axis(
                labelColor=cor_texto,
                titleColor=cor_texto,
                gridColor=cor_linha,
                domainColor=cor_linha,
                tickColor=cor_linha
            ).configure_view(
                stroke="transparent"
            )
            
            # IMPORTANTE: theme=None diz ao Streamlit para obedecer as nossas cores
            st.altair_chart(grafico, use_container_width=True, theme=None)
        else:
            st.info("Sem dados suficientes para gerar o gráfico neste período.")
            
    with col_resumo:
        st.subheader("Resumo por Motivo")
        st.caption("Contagem detalhada.")
        if not df.empty:
            resumo_df = df["Motivo"].value_counts().reset_index()
            resumo_df.columns = ["Motivo", "Quantidade"]
            
            # Aplicamos a função para escurecer a tabela
            st.dataframe(aplicar_tema_tabela(resumo_df), use_container_width=True)
        else:
            st.info("Nenhum atendimento registrado neste período.")

    st.divider()

    # --- RESUMO POR CIDADE ---
    st.subheader("Cidades com Mais Cancelamentos")
    st.caption("Volume de ocorrências agrupadas por localidade.")
    
    if not df.empty:
        # Conta quantas vezes cada cidade aparece
        resumo_cidade = df["Cidade"].value_counts().reset_index()
        resumo_cidade.columns = ["Cidade", "Total de Atendimentos"]
        
        # Exibe a tabela (já usando a sua função que escurece o tema, se necessário)
        st.dataframe(aplicar_tema_tabela(resumo_cidade), use_container_width=True)
    else:
        st.info("Nenhum dado de cidade registrado neste período.")
        
    st.divider()

    # Tabela de Desempenho
    st.subheader("Desempenho Individual por Colaborador")
    st.caption("Total de atendimentos e distribuição de motivos por agente.")
    
    if not df.empty:
        desempenho = pd.crosstab(df["Colaborador"], df["Motivo"], margins=True, margins_name="Total")
        
        # Aplicamos a função para escurecer a tabela
        st.dataframe(aplicar_tema_tabela(desempenho), use_container_width=True)
    else:
        st.info("Nenhum atendimento registrado para exibir desempenho.")
        
    st.divider()
    
    # --- NOVA TABELA: HISTÓRICO COMPLETO DE ATENDIMENTOS ---
    st.subheader("Histórico Detalhado de Atendimentos")
    st.caption("Últimos 10 registros da operação no período selecionado.")
    
    if not df.empty:
        # Puxando a coluna 'Cidade' e formatando a tabela base
        tabela_historico = df[["Data", "Colaborador", "ID", "Cliente", "Cidade", "Motivo", "Detalhes"]]
        tabela_historico.columns = [
            "Data/Hora", "Colaborador Responsável", "ID",  "Nome", "Cidade", "Motivo Principal", "Motivo Detalhado"
        ]
        
        # 1. Filtra os últimos 10 e inverte a ordem (.iloc[::-1]) para o mais novo ficar no topo!
        ultimos_10 = tabela_historico.tail(10).iloc[::-1]
        
        # Mostra a tabela principal enxuta
        st.dataframe(aplicar_tema_tabela(ultimos_10), use_container_width=True)
        
        # 2. Se houver mais de 10 registros, cria o menu expansível
        if len(tabela_historico) > 10:
            with st.expander("📂 Ampliar para lista completa de atendimentos"):
                # Mostra todos os dados do período, também do mais novo para o mais antigo
                tabela_completa = tabela_historico.iloc[::-1]
                st.dataframe(aplicar_tema_tabela(tabela_completa), use_container_width=True)
                
    else:
        st.info("Nenhuma ligação foi registrada neste período.")
# ---------------------------------------------------------
    # ÁREA DE EXCLUSÃO DE REGISTROS (Logo abaixo da tabela)
    # ---------------------------------------------------------
    st.write("") # Dá um pequeno respiro/espaçamento na tela
    st.markdown("#### 🗑️ Excluir Lançamento Incorreto")
    
    col1, col2, col3 = st.columns([2, 3, 5])
    
    with col1:
        # Campo para o usuário digitar o ID que deseja apagar
        id_apagar = st.text_input("ID", label_visibility="collapsed", placeholder="Digite o ID (ex: 2325)")
        
    with col2:
        if st.button("🗑️ Apagar Registro", use_container_width=True):
            if id_apagar:
                # Puxa o banco de dados atual
                banco_dados = st.session_state.atendimentos
                
                # Filtra o banco: Mantém todo mundo que tem o ID DIFERENTE do ID digitado
                # Convertemos ambos para texto (.astype(str)) para evitar erro de leitura
                banco_atualizado = banco_dados[banco_dados['ID'].astype(str) != id_apagar.strip()]
                
                # Se o tamanho do banco diminuiu, é porque achou e deletou o ID
                if len(banco_atualizado) < len(banco_dados):
                    st.session_state.atendimentos = banco_atualizado
                    st.rerun() # Atualiza a página na mesma hora e o registro some da tabela de cima!
                else:
                    st.error("❌ ID não encontrado no histórico.")
            else:
                st.warning("⚠️ Digite um ID antes de clicar.")    

# ---------------------------------------------------------
# TELA 3: COLABORADORES & ACESSOS 
# ---------------------------------------------------------
elif menu == "Colaboradores":
    # Inicializa as variáveis de controle na memória
    if "mostrar_form" not in st.session_state:
        st.session_state.mostrar_form = False
    if "editando_index" not in st.session_state:
        st.session_state.editando_index = None

    col_titulo, col_botao = st.columns([4, 1])
    with col_titulo:
        st.header("Colaboradores")
        st.caption("Gerencie agentes, supervisores e acessos ao sistema.")
    with col_botao:
        # Removido o emoji de adição
        if st.button("Novo Colaborador", use_container_width=True):
            st.session_state.mostrar_form = not st.session_state.mostrar_form
            st.session_state.editando_index = None # Fecha qualquer edição que estiver aberta
            st.rerun()
            
    st.write("")
    
    # Cria as abas de navegação (como pastas de arquivo)
    aba_agentes, aba_acessos = st.tabs(["Agentes", "Acessos ao Sistema"])
    
    # ==========================================
    # ABA 1: AGENTES (Seu código antigo indentado)
    # ==========================================
    with aba_agentes:
        # --- FORMULÁRIO DE NOVO COLABORADOR ---
        if st.session_state.mostrar_form:
            with st.container(border=True):
                with st.form("form_novo_colaborador", clear_on_submit=True):
                    st.subheader("Cadastrar Novo Colaborador")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        novo_nome = st.text_input("Nome do Colaborador *", placeholder="Ex: Maria Eduarda")
                    with col2:
                        novo_cargo = st.selectbox("Cargo", ["Operador", "Supervisor", "Gerente"])
                    with col3:
                        novo_status = st.selectbox("Status", ["Ativo", "Inativo"])
                    
                    if st.form_submit_button("Salvar Colaborador"):
                        if not novo_nome.strip():
                            st.error("Por favor, preencha o nome do colaborador.")
                        else:
                            nova_linha = pd.DataFrame([{"Nome": novo_nome, "Cargo": novo_cargo, "Status": novo_status}])
                            st.session_state.colaboradores = pd.concat([st.session_state.colaboradores, nova_linha], ignore_index=True)
                            st.session_state.mostrar_form = False
                            st.rerun()
        
        st.divider()
        
        # --- GRID DE COLABORADORES (CARDS) ---
        colaboradores_df = st.session_state.colaboradores
        cols = st.columns(3) # Grid de 3 colunas
        
        for index, row in colaboradores_df.iterrows():
            with cols[index % 3]:
                with st.container(border=True):
                    
                    # SE ESTE CARD ESTIVER EM MODO DE EDIÇÃO:
                    if st.session_state.editando_index == index:
                        
                        # -- BOTÃO DE EXCLUIR (LIXEIRA) NO CANTO SUPERIOR DIREITO --
                        col_vazia, col_lixeira = st.columns([4, 1])
                        with col_lixeira:
                            # A lixeira foi mantida pois age como um ícone de interface padrão
                            if st.button("🗑️", key=f"del_{index}", help="Excluir colaborador"):
                                st.session_state.colaboradores = st.session_state.colaboradores.drop(index).reset_index(drop=True)
                                st.session_state.editando_index = None
                                st.rerun()
                                
                        edit_nome = st.text_input("Nome", value=row["Nome"], key=f"edit_nome_{index}")
                        
                        cargos = ["Operador", "Supervisor", "Gerente"]
                        cargo_idx = cargos.index(row["Cargo"]) if row["Cargo"] in cargos else 0
                        edit_cargo = st.selectbox("Cargo", cargos, index=cargo_idx, key=f"edit_cargo_{index}")
                        
                        status_opts = ["Ativo", "Inativo"]
                        status_idx = status_opts.index(row["Status"]) if row["Status"] in status_opts else 0
                        edit_status = st.selectbox("Status", status_opts, index=status_idx, key=f"edit_status_{index}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            # Removido o emoji de disquete
                            if st.button("Salvar", key=f"save_{index}", use_container_width=True):
                                if edit_nome.strip():
                                    st.session_state.colaboradores.at[index, "Nome"] = edit_nome
                                    st.session_state.colaboradores.at[index, "Cargo"] = edit_cargo
                                    st.session_state.colaboradores.at[index, "Status"] = edit_status
                                    st.session_state.editando_index = None 
                                    st.rerun()
                                else:
                                    st.error("Nome não pode ficar vazio.")
                        with col_cancel:
                            # Removido o emoji de 'X'
                            if st.button("Cancelar", key=f"cancel_{index}", use_container_width=True):
                                st.session_state.editando_index = None 
                                st.rerun()
                                
                    # SE ESTIVER NO MODO NORMAL DE VISUALIZAÇÃO:
                    else:
                        st.subheader(row["Nome"])
                        
                        # Removido a variável status_icon que inseria o ✅ ou ❌
                        st.markdown(f"**Cargo:** {row['Cargo']} &nbsp;&nbsp; | &nbsp;&nbsp; **Status:** {row['Status']}")
                        
                        # Removido o emoji de lápis
                        if st.button("Editar", key=f"btn_edit_{index}", use_container_width=True):
                            st.session_state.editando_index = index
                            st.session_state.mostrar_form = False 
                            st.rerun()

    # ==========================================
    # ABA 2: ACESSOS AO SISTEMA
    # ==========================================
    with aba_acessos:
        with st.container(border=True):
            st.markdown("#### 👤 Autorizar Novo Acesso")
            st.caption("Crie um login para um colaborador acessar o sistema.")
            
            with st.form("form_novo_acesso", clear_on_submit=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    novo_nome = st.text_input("Nome", placeholder="Ex: João Silva")
                with col2:
                    novo_email = st.text_input("E-mail", placeholder="exemplo@superconnect.com.br")
                with col3:
                    nova_funcao = st.selectbox("Função", ["Operador", "Supervisor"])
                    
                nova_senha = st.text_input("Senha Temporária", placeholder="Defina uma senha", type="password")
                
                if st.form_submit_button("Salvar Acesso"):
                    if novo_nome and novo_email and nova_senha:
                        novo_user = {"Nome": novo_nome, "Email": novo_email, "Senha": nova_senha, "Funcao": nova_funcao}
                        st.session_state.usuarios = pd.concat([st.session_state.usuarios, pd.DataFrame([novo_user])], ignore_index=True)
                        st.success(f"Acesso criado para {novo_email}!")
                        st.rerun()
                    else:
                        st.error("Preencha todos os campos obrigatórios.")
        
        st.write("")
        with st.container(border=True):
            st.markdown("#### 🛡️ Usuários Autorizados")
            st.caption("Pessoas com acesso ao sistema. Remova para revogar o acesso.")
            
            for index, row in st.session_state.usuarios.iterrows():
                col_info, col_del = st.columns([8, 1])
                with col_info:
                    st.markdown(f"**{row['Email']}**")
                    st.caption(f"{row['Nome']} • {row['Funcao']}")
                with col_del:
                    # Impede o admin atual de deletar a própria conta acidentalmente
                    if row["Email"] != st.session_state.usuario_logado["Email"]:
                        if st.button("🗑️", key=f"del_user_{index}"):
                            st.session_state.usuarios = st.session_state.usuarios.drop(index).reset_index(drop=True)
                            st.rerun()
                st.divider()
# ---------------------------------------------------------
# TELA 4: RELATÓRIOS ANALÍTICOS
# ---------------------------------------------------------
elif menu == "Relatórios":
    st.header("Relatórios e Perdas Financeiras")
    st.caption("Filtre as variáveis para analisar o desempenho da operação e mapear a receita perdida.")
    
    df = st.session_state.atendimentos
    
    if not df.empty:
        # 1. PAINEL DE FILTROS COM MÚLTIPLAS COLUNAS E LIMPEZA
        with st.expander("🔍 Filtros de Busca", expanded=True):
            
            # --- FUNÇÃO DE CALLBACK (Zera tudo ANTES da tela recarregar) ---
            def zerar_filtros():
                st.session_state.f_colab = []
                st.session_state.f_status = []
                st.session_state.f_plano = []
                st.session_state.f_motivo = []
                st.session_state.f_cidade = []
                # Remove a data para forçar ela a voltar ao valor padrão
                if 'f_data' in st.session_state:
                    del st.session_state['f_data']
            
            # --- BOTÃO DE LIMPAR FILTROS ---
            col_btn, col_vazia = st.columns([2, 8])
            with col_btn:
                # Agora o botão usa o 'on_click' e não precisa mais do st.rerun()
                st.button("Limpar Filtros", on_click=zerar_filtros, use_container_width=True)

            st.write("") 
            
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                # Filtro de Data
                df['Data_Real'] = pd.to_datetime(df['Data'], format="%d/%m/%Y %H:%M")
                min_date = df['Data_Real'].dt.date.min()
                max_date = df['Data_Real'].dt.date.max()
                
                filtro_data = st.date_input(
                    "Período", 
                    value=[min_date, max_date], 
                    format="DD/MM/YYYY",
                    key='f_data' 
                )
                
                lista_colaboradores = st.session_state.colaboradores['Nome'].tolist()
                filtro_colaborador = st.multiselect("Colaborador Responsável", options=lista_colaboradores, key='f_colab')
                
            with col_f2:
                filtro_status = st.multiselect("Status da Retenção", options=["Cancelamento Concluído", "Cliente Retido/Revertido"], key='f_status')
                
                lista_planos_full = [
                    "Internet", "Câmera", "Chip", "TV", "Internet+Câmera", "Internet+Chip", 
                    "Internet+TV", "Câmera+Chip", "Câmera+TV", "Chip+TV", "Internet+Câmera+Chip", 
                    "Internet+Câmera+TV", "Internet+Chip+TV", "Câmera+Chip+TV", "Internet+Câmera+Chip+TV"
                ]
                filtro_plano = st.multiselect("Plano Cancelado", options=lista_planos_full, key='f_plano')
                
            with col_f3:
                filtro_motivo = st.multiselect("Motivo Principal", options=MOTIVOS, key='f_motivo')
                
                filtro_cidade = st.multiselect("Cidade", options=df['Cidade'].unique(), key='f_cidade')
        
        # APLICAÇÃO DOS FILTROS (Lógica de Cruzamento)
        df_filtrado = df.copy()
        
        if len(filtro_data) == 2:
            start_date, end_date = filtro_data
            mask_data = (df_filtrado['Data_Real'].dt.date >= start_date) & (df_filtrado['Data_Real'].dt.date <= end_date)
            df_filtrado = df_filtrado.loc[mask_data]
            
        if filtro_colaborador: df_filtrado = df_filtrado[df_filtrado['Colaborador'].isin(filtro_colaborador)]
        if filtro_status: df_filtrado = df_filtrado[df_filtrado['Status'].isin(filtro_status)]
        if filtro_plano: df_filtrado = df_filtrado[df_filtrado['Plano Cancelado'].isin(filtro_plano)]
        if filtro_motivo: df_filtrado = df_filtrado[df_filtrado['Motivo'].isin(filtro_motivo)]
        if filtro_cidade: df_filtrado = df_filtrado[df_filtrado['Cidade'].isin(filtro_cidade)]
        
        st.divider()
        
        # 2. PAINEL DE TOTALIZADORES (KPIs)
        st.subheader("Visão Geral do Período")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        total_cancelados = len(df_filtrado[df_filtrado['Status'] == "Cancelamento Concluído"])
        total_revertidos = len(df_filtrado[df_filtrado['Status'] == "Cliente Retido/Revertido"])
        receita_perdida = df_filtrado['Valor Perdido'].sum()
        
        with kpi1:
            st.metric(label="Total de Planos Cancelados", value=total_cancelados)
        with kpi2:
            # Exibe em formato monetário bonito
            st.metric(label="Receita Perdida (R$)", value=f"R$ {receita_perdida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with kpi3:
            st.metric(label="Reversões Concluídas", value=total_revertidos)
            
        st.divider()
        
        # 3. TABELA COM O RESULTADO DOS FILTROS
        st.markdown("#### Detalhamento dos Lançamentos")
        
        # Remove a coluna técnica e transforma a 'Data' na coluna principal para esconder os números (0, 1, 2...)
        df_exibicao = df_filtrado.drop(columns=['Data_Real']).set_index('Data')
        
        # O st.dataframe agora está forçado a ficar transparente pelo CSS
        st.dataframe(aplicar_tema_tabela(df_exibicao), use_container_width=True)
        
    else:
        st.info("Nenhuma ligação foi registrada no sistema ainda.")
