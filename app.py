import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import datetime
import altair as alt
from supabase import create_client, Client

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Super Connect | Retenção", layout="wide", page_icon="📉", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INICIALIZAÇÃO DO BANCO DE DADOS (SUPABASE)
# ---------------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

@st.cache_data(ttl=5) 
def carregar_usuarios():
    resposta = supabase.table("usuarios").select("*").execute()
    if not resposta.data:
        return pd.DataFrame(columns=["ID", "Nome", "Email", "Senha", "Funcao"])
    df = pd.DataFrame(resposta.data)
    return df.rename(columns={"id": "ID", "nome": "Nome", "email": "Email", "senha": "Senha", "funcao": "Funcao"})

@st.cache_data(ttl=5)
def carregar_colaboradores():
    resposta = supabase.table("colaboradores").select("*").execute()
    if not resposta.data:
        return pd.DataFrame(columns=["ID", "Nome", "Cargo", "Status"])
    df = pd.DataFrame(resposta.data)
    return df.rename(columns={"id": "ID", "nome": "Nome", "cargo": "Cargo", "status": "Status"})

@st.cache_data(ttl=5)
def carregar_atendimentos():
    resposta = supabase.table("atendimentos").select("*").execute()
    if not resposta.data:
        return pd.DataFrame(columns=["Data", "Cliente", "ID", "Cidade", "Plano Cancelado", 
                                     "Valor Perdido", "Status", "Motivo", "Detalhes", "Colaborador"])
    df = pd.DataFrame(resposta.data)
    df = df.rename(columns={
        "data": "Data", "cliente": "Cliente", "id_cliente": "ID", "cidade": "Cidade", 
        "plano_cancelado": "Plano Cancelado", "valor_perdido": "Valor Perdido", 
        "status": "Status", "motivo": "Motivo", "detalhes": "Detalhes", "colaborador": "Colaborador",
        "tipo_cancelamento": "tipo_cancelamento", "qtd_pontos": "qtd_pontos"
    })
    return df

st.session_state.usuarios = carregar_usuarios()
st.session_state.colaboradores = carregar_colaboradores()
st.session_state.atendimentos = carregar_atendimentos()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usuario_logado = None

MOTIVOS = ["Insatisfação", "Mudança de endereço", "Inviabilidade", "Problemas financeiros", "Revertido", "Outros"]

# ---------------------------------------------------------
# 3. TELA DE LOGIN 
# ---------------------------------------------------------
if not st.session_state.logged_in:
    import base64
    def get_base64_of_bin_file(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except FileNotFoundError:
            return ""

    img_base64 = get_base64_of_bin_file("background.png")

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover; background-position: center top; background-repeat: no-repeat; background-attachment: fixed;
        }}
        section[data-testid="stSidebar"] {{ display: none !important; }}
        div[data-testid="stForm"] {{
            background-color: rgba(15, 23, 42, 0.85) !important; border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important; 
            padding: 30px 20px !important; margin-top: 200px !important; 
        }}
        div[data-testid="stForm"] p, div[data-testid="stForm"] label {{ color: #f8fafc !important; }}
        div[data-testid="stFormSubmitButton"] button {{ background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #475569 !important; }}
        div[data-testid="stFormSubmitButton"] button p {{ color: #f8fafc !important; }}
        div[data-testid="stFormSubmitButton"] button:hover {{ border-color: #39ff14 !important; background-color: #0f172a !important; }}
        div[data-testid="stFormSubmitButton"] button:hover p {{ color: #39ff14 !important; }}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
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
    st.stop()
    
# ---------------------------------------------------------
# 4. MENU LATERAL (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
        .subtitulo-sidebar { text-align: center; font-size: 14px; margin-bottom: 15px; font-weight: 500; }
        </style>
    """, unsafe_allow_html=True) 

    st.image("images-Photoroom.png", use_container_width=True)
    st.markdown('<div class="subtitulo-sidebar" style="margin-top: -15px; margin-bottom: 20px;">RETENÇÃO E CANCELAMENTO</div>', unsafe_allow_html=True)
    st.divider()

    funcao_atual = st.session_state.usuario_logado["Funcao"]
    
    if funcao_atual == "Supervisor":
        opcoes_menu = ["Novo Atendimento", "Dashboard", "Colaboradores", "Relatórios"]
        icones_menu = ["headset", "grid", "people", "graph-up-arrow"]
    else:
        opcoes_menu = ["Novo Atendimento", "Dashboard"]
        icones_menu = ["headset", "grid"]

    menu = option_menu(
        menu_title=None, 
        options=opcoes_menu, 
        icons=icones_menu, 
        default_index=0,
        styles={
            "container": { "padding": "0!important", "border": "none", "background-color": "transparent" },
            "nav-link": { "font-family": "'Bebas Neue', sans-serif", "font-size": "18px", "text-align": "left", "margin": "8px 0px" }
        }
    )
    
    st.divider()
    st.caption(f"👤 **{st.session_state.usuario_logado['Nome']}** ({funcao_atual})")
    
    if st.button("Sair", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.usuario_logado = None
        st.rerun()

    st.markdown('<div style="text-align: center; margin-top: 30px; font-size: 12px; opacity: 0.7;">v1.0 • Setor de Retenção</div>', unsafe_allow_html=True)

st.write("")
st.write("")

# ---------------------------------------------------------
# 5. TELA 1: NOVO ATENDIMENTO 
# ---------------------------------------------------------
if menu == "Novo Atendimento":
    st.header("Registrar Atendimento")
    st.caption("Preencha os dados após cada ligação. A data e hora são registradas automaticamente.")
    
    with st.container(border=True):
        with st.form("form_registro", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                cliente = st.text_input("Nome do Cliente *", placeholder="Ex.: João da Silva")
            with col2:
                id_cliente = st.text_input("ID do Cliente *", placeholder="Ex.: 10243578")
            with col3:
                cidade = st.text_input("Cidade *", placeholder="Ex.: Nome da cidade")

            col_plano, col_valor, col_status = st.columns(3)
            with col_plano:
                lista_planos = [
                    "Selecione o plano...", "Internet", "Câmera", "Chip", "TV", "Internet+Câmera", "Internet+Chip", 
                    "Internet+TV", "Câmera+Chip", "Câmera+TV", "Chip+TV", "Internet+Câmera+Chip", 
                    "Internet+Câmera+TV", "Internet+Chip+TV", "Câmera+Chip+TV", "Internet+Câmera+Chip+TV"
                ]
                plano_cancelado = st.selectbox("Plano Alvo do Cancelamento *", lista_planos)
            with col_valor:
                valor_perdido = st.text_input("Valor em Risco/Perdido (R$) *", placeholder="Ex.: 150,50")
            with col_status:
                status_retencao = st.selectbox("Status Final da Retenção *", ["Selecione...", "Cancelamento Concluído", "Cliente Retido/Revertido"])

            col_motivo, col_migrado = st.columns(2)
            with col_motivo:
                motivo = st.selectbox("Motivo Principal *", ["Selecione o motivo principal..."] + MOTIVOS)
            with col_migrado:
                lista_migrados = ["Não se aplica (Cancelado)"] + lista_planos[1:]
                plano_migrado = st.selectbox("Plano Migrado (Em caso de Retenção)", lista_migrados)

            col_tipo, col_pontos = st.columns(2)
            with col_tipo:
                tipo_cancelamento = st.radio("Tipo de Cancelamento *", ["Total", "Parcial"], horizontal=True)
            with col_pontos:
                qtd_pontos = 0  
                if tipo_cancelamento == "Parcial":
                    qtd_pontos = st.number_input("Quantidade de Pontos Cancelados *", min_value=1, step=1)

            try:
                nomes = st.session_state.colaboradores['Nome'].tolist()
            except:
                nomes = list(st.session_state.colaboradores)
                
            colaborador = st.selectbox("Colaborador Responsável *", ["Selecione o colaborador..."] + nomes)
            detalhes = st.text_area("Motivo Detalhado (Resumo)", placeholder="Resumo da ligação...")
            
            col_submit, col_clear = st.columns([8, 1])
            with col_submit:
                submit = st.form_submit_button("Registrar Atendimento", use_container_width=True)
            with col_clear:
                st.form_submit_button("Limpar", use_container_width=True)
                
            if submit:
                # 1. Trava de campos vazios
                if (not cliente or not id_cliente or not cidade.strip() or not detalhes.strip() or 
                    motivo.startswith("Selecione") or colaborador.startswith("Selecione") or 
                    plano_cancelado.startswith("Selecione") or status_retencao.startswith("Selecione")):
                    st.warning("⚠️ Por favor, preencha todos os campos obrigatórios antes de submeter o atendimento.")
                
                # 2. A NOVA TRAVA: Verifica se o ID digitado tem apenas números
                elif not id_cliente.strip().isdigit():
                    st.error("❌ O campo 'ID do Cliente' deve conter APENAS NÚMEROS. Verifique se você não inverteu o Nome com o ID.")
                
                else:
                    try:
                        valor_formatado = float(valor_perdido.replace(".", "").replace(",", "."))
                        data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                        
                        dados_para_nuvem = {
                            "data": data_atual, 
                            "cliente": cliente, 
                            "id_cliente": int(id_cliente.strip()), # Converte garantido para o formato do Supabase
                            "cidade": cidade.title(),
                            "plano_cancelado": plano_cancelado, 
                            "valor_perdido": valor_formatado, 
                            "status": status_retencao,
                            "motivo": motivo, 
                            "detalhes": detalhes, 
                            "colaborador": colaborador, 
                            "tipo_cancelamento": tipo_cancelamento, 
                            "qtd_pontos": qtd_pontos
                        }
                        
                        supabase.table("atendimentos").insert(dados_para_nuvem).execute()
                        st.cache_data.clear() 
                        st.session_state.atendimentos = carregar_atendimentos()
                        st.success("✅ Atendimento registrado e salvo na nuvem com sucesso!")
                    except ValueError:
                        st.error("⚠️ Digite um valor válido no formato 150,50 no campo 'Valor em Risco/Perdido'.")
                    except Exception as e:
                        st.error(f"Erro ao salvar na nuvem: {e}")
                    
# ---------------------------------------------------------
# 6. TELA 2: DASHBOARD
# ---------------------------------------------------------
elif menu == "Dashboard":
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
    
    df = st.session_state.atendimentos.copy()
    if not df.empty:
        df["Data_Calculo"] = pd.to_datetime(df["Data"], format="%d/%m/%Y %H:%M").dt.date
        df = df[(df["Data_Calculo"] >= data_inicio) & (df["Data_Calculo"] <= data_fim)]
        if filtro_colab != "Todos":
            df = df[df["Colaborador"] == filtro_colab]
    
    total_atendimentos = len(df)
    retidos = len(df[df["Motivo"] == "Revertido"]) if not df.empty else 0
    cancelados = total_atendimentos - retidos
    taxa_retencao = f"{(retidos / total_atendimentos * 100):.1f}%" if total_atendimentos > 0 else "0.0%"

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

    col_grafico, col_resumo = st.columns([2, 1])
    with col_grafico:
        st.subheader("Cancelamentos por Motivo Principal")
        if not df.empty:
            dados_grafico = df["Motivo"].value_counts().reset_index()
            dados_grafico.columns = ["Motivo", "Quantidade"]
            grafico = alt.Chart(dados_grafico).mark_bar(size=35, cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X('Motivo', sort='-y', title=None, axis=alt.Axis(labelAngle=-40)),
                y=alt.Y('Quantidade', title=None),
                color=alt.Color('Motivo', legend=None, scale=alt.Scale(scheme='set2')), tooltip=['Motivo', 'Quantidade']
            ).properties(height=350)
            st.altair_chart(grafico, use_container_width=True, theme="streamlit")
        else:
            st.info("Sem dados suficientes para gerar o gráfico neste período.")
            
    with col_resumo:
        st.subheader("Resumo por Motivo")
        if not df.empty:
            resumo_df = df["Motivo"].value_counts().reset_index()
            resumo_df.columns = ["Motivo", "Quantidade"]
            st.dataframe(resumo_df, use_container_width=True)
        else:
            st.info("Nenhum atendimento registrado neste período.")

    st.divider()
    st.subheader("Cidades com Mais Cancelamentos")
    if not df.empty:
        resumo_cidade = df["Cidade"].value_counts().reset_index()
        resumo_cidade.columns = ["Cidade", "Total de Atendimentos"]
        st.dataframe(resumo_cidade, use_container_width=True)
        
    st.divider()
    st.subheader("Desempenho Individual por Colaborador")
    if not df.empty:
        desempenho = pd.crosstab(df["Colaborador"], df["Motivo"], margins=True, margins_name="Total")
        st.dataframe(desempenho, use_container_width=True)
        
    st.divider()
    st.subheader("Histórico Detalhado de Atendimentos")
    if not df.empty:
        tabela_historico = df[["Data", "Colaborador", "ID", "Cliente", "Cidade", "Motivo", "Detalhes"]]
        tabela_historico.columns = ["Data/Hora", "Colaborador Responsável", "ID",  "Nome", "Cidade", "Motivo Principal", "Motivo Detalhado"]
        ultimos_10 = tabela_historico.tail(10).iloc[::-1]
        st.dataframe(ultimos_10, use_container_width=True)
        
        if len(tabela_historico) > 10:
            with st.expander("📂 Ampliar para lista completa de atendimentos"):
                st.dataframe(tabela_historico.iloc[::-1], use_container_width=True)
    else:
        st.info("Nenhuma ligação foi registrada neste período.")

    st.write("") 
    st.markdown("#### 🗑️ Excluir Lançamento Incorreto")
    col1, col2, col3 = st.columns([2, 3, 5])
    with col1:
        id_apagar = st.text_input("ID", label_visibility="collapsed", placeholder="Digite o ID (ex: 2325)")
    with col2:
        if st.button("🗑️ Apagar Registro", use_container_width=True):
            if id_apagar:
                try:
                    # 1. Apaga do banco de dados na nuvem exatamente como fizemos nos Colaboradores
                    supabase.table("atendimentos").delete().eq("id_cliente", id_apagar.strip()).execute()
                    
                    # 2. Atualiza a memória instantaneamente e recarrega a tela
                    st.cache_data.clear() 
                    st.session_state.atendimentos = carregar_atendimentos()
                    st.rerun() 
                except Exception as e:
                    st.error(f"Erro ao tentar apagar na nuvem: {e}")
            else:
                st.warning("⚠️ Digite um ID antes de clicar.")  

# ---------------------------------------------------------
# 7. TELA 3: COLABORADORES & ACESSOS 
# ---------------------------------------------------------
elif menu == "Colaboradores":
    if "mostrar_form" not in st.session_state:
        st.session_state.mostrar_form = False
    if "editando_index" not in st.session_state:
        st.session_state.editando_index = None

    col_titulo, col_botao = st.columns([4, 1])
    with col_titulo:
        st.header("Colaboradores")
        st.caption("Gerencie agentes, supervisores e acessos ao sistema.")
    with col_botao:
        if st.button("Novo Colaborador", use_container_width=True):
            st.session_state.mostrar_form = not st.session_state.mostrar_form
            st.session_state.editando_index = None 
            st.rerun()
            
    aba_agentes, aba_acessos = st.tabs(["Agentes", "Acessos ao Sistema"])
    
    with aba_agentes:
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
                            dados_colab = { "nome": novo_nome.strip(), "cargo": novo_cargo, "status": novo_status }
                            try:
                                supabase.table("colaboradores").insert(dados_colab).execute()
                                st.cache_data.clear()
                                st.session_state.colaboradores = carregar_colaboradores()
                                st.session_state.mostrar_form = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar na nuvem: {e}")
        
        st.divider()
        colaboradores_df = st.session_state.colaboradores
        cols = st.columns(3) 
        
        for index, row in colaboradores_df.iterrows():
            with cols[index % 3]:
                with st.container(border=True):
                    if st.session_state.editando_index == index:
                        col_vazia, col_lixeira = st.columns([4, 1])
                        with col_lixeira:
                            if st.button("🗑️", key=f"del_{index}"):
                                try:
                                    supabase.table("colaboradores").delete().eq("id", row["ID"]).execute()
                                    st.cache_data.clear()
                                    st.session_state.colaboradores = carregar_colaboradores()
                                    st.session_state.editando_index = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir na nuvem: {e}")
                                
                        edit_nome = st.text_input("Nome", value=row["Nome"], key=f"edit_nome_{index}")
                        cargos = ["Operador", "Supervisor", "Gerente"]
                        cargo_idx = cargos.index(row["Cargo"]) if row["Cargo"] in cargos else 0
                        edit_cargo = st.selectbox("Cargo", cargos, index=cargo_idx, key=f"edit_cargo_{index}")
                        status_opts = ["Ativo", "Inativo"]
                        status_idx = status_opts.index(row["Status"]) if row["Status"] in status_opts else 0
                        edit_status = st.selectbox("Status", status_opts, index=status_idx, key=f"edit_status_{index}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Salvar", key=f"save_{index}", use_container_width=True):
                                if edit_nome.strip():
                                    dados_update = { "nome": edit_nome.strip(), "cargo": edit_cargo, "status": edit_status }
                                    try:
                                        supabase.table("colaboradores").update(dados_update).eq("id", row["ID"]).execute()
                                        st.cache_data.clear()
                                        st.session_state.colaboradores = carregar_colaboradores()
                                        st.session_state.editando_index = None 
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar na nuvem: {e}")
                                else:
                                    st.error("Nome não pode ficar vazio.")
                        with col_cancel:
                            if st.button("Cancelar", key=f"cancel_{index}", use_container_width=True):
                                st.session_state.editando_index = None 
                                st.rerun()
                    else:
                        st.subheader(row["Nome"])
                        st.markdown(f"**Cargo:** {row['Cargo']} &nbsp;&nbsp; | &nbsp;&nbsp; **Status:** {row['Status']}")
                        if st.button("Editar", key=f"btn_edit_{index}", use_container_width=True):
                            st.session_state.editando_index = index
                            st.session_state.mostrar_form = False 
                            st.rerun()

    with aba_acessos:
        with st.container(border=True):
            st.markdown("#### 👤 Autorizar Novo Acesso")
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
                        dados_usuario = { "nome": novo_nome, "email": novo_email, "senha": nova_senha, "funcao": nova_funcao }
                        try:
                            supabase.table("usuarios").insert(dados_usuario).execute()
                            st.cache_data.clear()
                            st.session_state.usuarios = carregar_usuarios()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar na nuvem: {e}")
                    else:
                        st.error("⚠️ Preencha todos os campos obrigatórios.")
        
        st.write("") 
    st.markdown("#### 🗑️ Excluir Lançamento Incorreto")
    col1, col2, col3 = st.columns([2, 3, 5])
    with col1:
        id_apagar = st.text_input("ID", label_visibility="collapsed", placeholder="Digite o ID (ex: 2325)")
    with col2:
        if st.button("🗑️ Apagar Registro", use_container_width=True):
            if id_apagar:
                # 1. Pega o que foi digitado e limpa imperfeições
                id_limpo_input = str(id_apagar).strip().replace(".0", "")
                
                # 2. Busca na nossa tabela carregada
                df_atend = st.session_state.atendimentos
                
                if not df_atend.empty and "id" in df_atend.columns:
                    # Limpa a coluna da tabela para garantir uma comparação perfeita
                    ids_tabela = df_atend["ID"].astype(str).str.replace(".0", "", regex=False).str.strip()
                    
                    # Encontra a linha exata
                    linhas_encontradas = df_atend[ids_tabela == id_limpo_input]
                    
                    if not linhas_encontradas.empty:
                        try:
                            # 3. Pega a CHAVE PRIMÁRIA interna do banco
                            id_real_banco = int(linhas_encontradas.iloc[0]["id"])
                            
                            # 4. Manda o tiro certeiro no banco usando a chave primária
                            supabase.table("atendimentos").delete().eq("id", id_real_banco).execute()
                            
                            # Atualiza a tela
                            st.cache_data.clear() 
                            st.session_state.atendimentos = carregar_atendimentos()
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Erro ao tentar apagar na nuvem: {e}")
                    else:
                        st.error("❌ O ID digitado não foi encontrado na tabela.")
            else:
                st.warning("⚠️ Digite um ID antes de clicar.")

# ---------------------------------------------------------
# 8. TELA 4: RELATÓRIOS ANALÍTICOS
# ---------------------------------------------------------
elif menu == "Relatórios":
    st.header("Relatórios e Perdas Financeiras")
    st.caption("Filtre as variáveis para analisar o desempenho da operação e mapear a receita perdida.")
    
    df = st.session_state.atendimentos
    if not df.empty:
        if "tipo_cancelamento" not in df.columns:
            df["tipo_cancelamento"] = "Não Informado"
        else:
            df["tipo_cancelamento"] = df["tipo_cancelamento"].fillna("Não Informado")

        with st.expander("🔍 Filtros de Busca", expanded=True):
            def zerar_filtros():
                st.session_state.f_colab = []
                st.session_state.f_status = []
                st.session_state.f_plano = []
                st.session_state.f_motivo = []
                st.session_state.f_cidade = []
                st.session_state.f_tipo = [] 
                if 'f_data' in st.session_state:
                    del st.session_state['f_data']
            
            col_btn, col_vazia = st.columns([2, 8])
            with col_btn:
                st.button("Limpar Filtros", on_click=zerar_filtros, use_container_width=True)
            st.write("") 
            
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                df['Data_Real'] = pd.to_datetime(df['Data'], format="%d/%m/%Y %H:%M")
                min_date = df['Data_Real'].dt.date.min()
                max_date = df['Data_Real'].dt.date.max()
                filtro_data = st.date_input("Período", value=[min_date, max_date], format="DD/MM/YYYY", key='f_data')
                
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
                filtro_tipo = st.multiselect("Tipo de Cancelamento", options=["Total", "Parcial", "Não Informado"], key='f_tipo')
                
            with col_f3:
                filtro_motivo = st.multiselect("Motivo Principal", options=MOTIVOS, key='f_motivo')
                filtro_cidade = st.multiselect("Cidade", options=df['Cidade'].unique(), key='f_cidade')
        
        df_filtrado = df.copy()
        if len(filtro_data) == 2:
            start_date, end_date = filtro_data
            mask_data = (df_filtrado['Data_Real'].dt.date >= start_date) & (df_filtrado['Data_Real'].dt.date <= end_date)
            df_filtrado = df_filtrado.loc[mask_data]
            
        if filtro_colaborador:
            df_filtrado = df_filtrado[df_filtrado['Colaborador'].isin(filtro_colaborador)]
        if filtro_status:
            df_filtrado = df_filtrado[df_filtrado['Status'].isin(filtro_status)]
        if filtro_plano:
            df_filtrado = df_filtrado[df_filtrado['Plano Cancelado'].isin(filtro_plano)]
        if filtro_motivo:
            df_filtrado = df_filtrado[df_filtrado['Motivo'].isin(filtro_motivo)]
        if filtro_cidade:
            df_filtrado = df_filtrado[df_filtrado['Cidade'].isin(filtro_cidade)]
        if filtro_tipo:
            df_filtrado = df_filtrado[df_filtrado['tipo_cancelamento'].isin(filtro_tipo)]
        
        st.divider()
        kpi1, kpi2, kpi3 = st.columns(3)
        total_cancelados = len(df_filtrado[df_filtrado['Status'] == "Cancelamento Concluído"])
        total_revertidos = len(df_filtrado[df_filtrado['Status'] == "Cliente Retido/Revertido"])
        receita_perdida = df_filtrado['Valor Perdido'].sum()
        
        with kpi1:
            st.metric(label="Total de Planos Cancelados", value=total_cancelados)
        with kpi2:
            st.metric(label="Receita Perdida (R$)", value=f"R$ {receita_perdida:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with kpi3:
            st.metric(label="Reversões Concluídas", value=total_revertidos)
            
        st.divider()
        st.markdown("#### Detalhamento dos Lançamentos")
        df_exibicao = df_filtrado.drop(columns=['Data_Real']).set_index('Data')
        st.dataframe(df_exibicao, use_container_width=True)
    else:
        st.info("Nenhuma ligação foi registrada no sistema ainda.")
