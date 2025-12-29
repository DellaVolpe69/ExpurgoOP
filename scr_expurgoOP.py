import sys
import subprocess
import importlib.util
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path, PureWindowsPath
import itertools
from requests_oauthlib import OAuth2Session
import time
import requests
import io
import tempfile
from urllib.parse import urlsplit, quote
import os
import streamlit.components.v1 as components
import getpass
from io import BytesIO

# --- LINK DIRETO DA IMAGEM NO GITHUB ---
url_imagem = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/AppBackground02.png"
url_logo = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/DellaVolpeLogoBranco.png"
fox_image = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/Foxy4.png"

###### CONFIGURAR O TÍTULO DA PÁGINA #######
st.set_page_config(
    page_title="Expurgos OP",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    f"""
    <style>
    /* Remove fundo padrão dos elementos de cabeçalho que às vezes ‘brigam’ com o BG */
    header, [data-testid="stHeader"] {{
        background: transparent;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>
/* Forçar cor branca em qualquer texto dentro de markdown ou write */
/* p, span, div, label { */
p, label {
    color: #EDEBE6 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== Seletores amplos para pegar warnings/alerts em várias versões do Streamlit ===== */

/* Container genérico (várias builds usam esse data-testid) */
div[data-testid="stNotificationContent"],
div[data-testid="stNotification"],
div[data-testid="stAlert"],
div[class*="stNotification"],
div[class*="stAlert"],
div[role="alert"] {
    color: #EDEBE6 !important;         /* cor do texto */
}

/* Pegar explicitamente parágrafos/spans dentro do warning (onde o texto costuma estar) */
div[data-testid="stNotificationContent"] p,
div[data-testid="stNotificationContent"] span,
div[role="alert"] p,
div[role="alert"] span,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: #EDEBE6 !important;
}

/* Algumas builds colocam o texto dentro de elementos com classe .stMarkdown */
div[data-testid="stNotificationContent"] .stMarkdown,
div[role="alert"] .stMarkdown {
    color: #EDEBE6 !important;
}

/* Força também em labels e botões filhos (caso o warning tenha estruturas internas) */
div[data-testid="stNotification"] label,
div[role="alert"] label,
div[data-testid="stNotification"] button,
div[role="alert"] button {
    color: #EDEBE6 !important;
}
</style>
""", unsafe_allow_html=True)

##########################################
###### CARREGAR MÓDULOS E PARQUETS #######
# Caminho local onde o módulo será baixado
modulos_dir = Path(__file__).parent / "Modulos"

# Se o diretório ainda não existir, faz o clone direto do GitHub
if not modulos_dir.exists():
    print("📥 Clonando repositório Modulos do GitHub...")
    subprocess.run([
        "git", "clone",
        "https://github.com/DellaVolpe69/Modulos.git",
        str(modulos_dir)
    ], check=True)

# Garante que o diretório está no caminho de importação
if str(modulos_dir) not in sys.path:
    sys.path.insert(0, str(modulos_dir))

# Agora importa o módulo normalmente
from Modulos import AzureLogin

from Modulos import ConectionSupaBase
###################################
import Modulos.Minio.examples.MinIO as meu_minio

#from Modulos.Minio.examples.meu_minio import read_file, listar_anexos, manager  # ajuste o caminho se necessário
# 🔗 Conexão com o Supabase
supabase = ConectionSupaBase.conexao()

# Inicializa o estado da página
if "pagina" not in st.session_state:
    st.session_state.pagina = "menu"

# Funções para trocar de página
def ir_para_cadastrarManual():
    st.session_state.pagina = "CadastrarManual"
    
def ir_para_cadastrarEmMassa():
    st.session_state.pagina = "CadastrarEmMassa"

def ir_para_editar():
    st.session_state.pagina = "Editar"

# --- CSS personalizado ---
st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                        url("{url_imagem}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Inputs padrão: text_input, number_input, date_input, etc */
        input, textarea {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        
        /* Selectbox (parte fechada) */
        .stSelectbox div[data-baseweb="select"] > div {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        
        /* Date input container */
        .stDateInput input {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}

        .stButton > button {{
            background-color: #FF5D01 !important;
            color: #EDEBE6 !important;
            border: 2px solid white !important;
            padding: 0.6em 1.2em;
            border-radius: 10px !important;
            font-size: 1rem;
            font-weight: 500;
            font-color: #EDEBE6 !important;
            cursor: pointer;
            transition: 0.2s ease;
            text-decoration: none !important;   /* 👈 AQUI remove de vez */
            display: inline-block;
        }}
        .stButton > button:hover {{
            background-color: #993700 !important;
            color: #FF5D01 !important;
            transform: scale(1.03);
            font-color: #FF5D01 !important;
            border: 2px solid #FF5D01 !important;
        }}

        /* RODAPÉ FIXO */
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.6);
            color: white;
            text-align: center;
            font-size: 14px;
            padding: 8px 0;
            text-shadow: 1px 1px 2px black;
        }}
        .footer a {{
            color: #FF5D01;
            text-decoration: none;
            font-weight: bold;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE RODAPÉ ---
def rodape():
    st.markdown("""
        <div class="footer">
            © 2025 <b>Della Volpe</b> | Desenvolvido por <a href="#">Raphael Chiavegati Oliveira</a>
        </div>
    """, unsafe_allow_html=True)

##################################################################
##################### FUNÇÕES DO FORMULÁRIO ######################
##################################################################

# Função para carregar dados
def carregar_dados():
   data = supabase.table("ExpurgoOP").select("*").execute()
   return pd.DataFrame(data.data)

# Criar arquivo modelo Excel
def gerar_modelo_excel():
    colunas = ["Data", "Numero do documento", "Justificativa"]
    df_modelo = pd.DataFrame(columns=colunas)
    buffer = BytesIO()
    df_modelo.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

# Função para inserir
def inserir_registro_manual(
    numero,
    tipo,
    justificativa,
    data_selecionada,
    usuario
):

    # -----------------------------
    # 🚀 Enviar ao Supabase
    # -----------------------------
    res = supabase.table("ExpurgoOP").insert({
        "NUMERO_DOC": numero,
        "TIPO_DOC": tipo,
        "JUSTIFICATIVA": justificativa,
        "DATA": str(data_selecionada),
        "USUARIO": usuario
    }).execute()
    
    return res
    
def inserir_registro_em_massa(df, tipo, usuario):
    """
    Insere vários registros no Supabase vindos de um DataFrame do Excel.
    
    df   -> DataFrame com as colunas: "Data", "Numero do documento", "Justificativa"
    tipo -> string escolhida pelo usuário no Streamlit (mesmo campo da função manual)
    """
    
    registros = []

    for _, row in df.iterrows():
        registros.append({
            "NUMERO_DOC": str(row["Numero do documento"]),
            "TIPO_DOC": tipo,
            "JUSTIFICATIVA": row["Justificativa"],
            "DATA": str(row["Data"]),  # garante formato serializável
            "USUARIO": usuario
        })

    # Enviar todos de uma vez (mais rápido que um por um)
    res = supabase.table("ExpurgoOP").insert(registros).execute()
    
    return res

# Função para atualizar
def atualizar_registro(id,
                        numero_doc,
                        tipo_doc,
                        justificativa,
                        data_selecionada):
    
    supabase.table("ExpurgoOP").update({
        "NUMERO_DOC": numero_doc,
        "TIPO_DOC": tipo_doc,
        "JUSTIFICATIVA": justificativa,
        "DATA": str(data_selecionada)
    }).eq("ID", id).execute()
    st.success("✏️ Registro atualizado com sucesso!")
    
# Função para excluir
def excluir_registro(id):
    supabase.table("ExpurgoOP").delete().eq("ID", id).execute()
    st.success("🗑️ Registro excluído com sucesso!")

# Função para limpar campos invisíveis
def limpar_campos():
    tipo_atual = st.session_state.get("tipo")
    
# Função para verificar se já existe um cadastro igual
def verificar_existencia(numero, tipo, justificativa, data_selecionada):
    result = (
        supabase.table("ExpurgoOP")
        .select("ID")
        .eq("NUMERO_DOC", numero)
        .eq("TIPO_DOC", tipo)
        .eq("JUSTIFICATIVA", justificativa)
        .eq("DATA", data_selecionada)
        .execute()
    )

    # Se encontrar alguma linha → já existe
    return len(result.data) > 0

###########################################################################
###########################################################################

#df_filial = MinIO.read_file('dados/CV_FILIAL.parquet', 'calculation-view')[['SALESORG', 'TXTMD_1']].drop_duplicates().reset_index(drop=True)
#df_filial = df_filial[['SALESORG', 'TXTMD_1']].drop_duplicates().reset_index(drop=True)

##################################################################
##################################################################
##################################################################

# --- MENU PRINCIPAL ---
if st.session_state.pagina == "menu":
    st.markdown(f"""
        <div class="header" style="text-align: center; padding-top: 2em;">
            <img src="{url_logo}" alt="Logo Della Volpe" 
                 style="width: 40%; max-width: 200px; height: auto; margin-bottom: 10px;">
            <h1 style="color: #EDEBE6; text-shadow: 1px 1px 3px black;">
                Expurgo OP
            </h1>
        </div>
    """, unsafe_allow_html=True)
    # Espaço antes dos botões (ajuste quantos <br> quiser)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("Registro Manual", use_container_width=True, on_click=ir_para_cadastrarManual)
        st.button("Registro em Massa", use_container_width=True, on_click=ir_para_cadastrarEmMassa)
        st.button("Editar", use_container_width=True, on_click=ir_para_editar)
    rodape()

# --- PÁGINA CADASTRAR MANUAL---
if st.session_state.pagina == "CadastrarManual":
    st.markdown(
    "<h1 style='text-align: center; color: #EDEBE6; text-shadow: 1px 1px 3px black;'>"
    "📝 Expurgo OP"
    "</h1>",
    unsafe_allow_html=True
)
    #st.write("👤 Usuário logado:", st.session_state.get("user_name"))

    ############################################

    st.markdown(
    "<h1 style='text-align: center; color: #EDEBE6; text-shadow: 1px 1px 3px black;'>"
    "Inserir registro manualmente"
    "</h1>",
    unsafe_allow_html=True
)
    numero = st.text_input("Número do documento")
    tipo = st.selectbox("Tipo do documento", ["OEF", "OF", "SEFAZ NOTA", "SEFAZ CTE"], key="tipo_manual")
    data_selecionada = st.date_input("Selecione uma data",
                                    value=date.today(),  # valor inicial
                                    min_value=date(2020, 1, 1),  # data mínima
                                    max_value=date(2030, 12, 31),  # data máxima
                                    key="campo_data"  # chave única (evita erro de ID duplicado)
                                    )
    justificativa = st.text_area("Justificativa")
    ######### ANEXO #########
    #anexo = st.file_uploader("Anexo", type=["pdf", "docx", "xlsx", "jpg", "png"], key="anexo_manual")
    
    st.markdown("""
        <style>
        /* Texto do label do file_uploader */
        div[data-testid="stFileUploader"] div {
            color: #EDEBE6 !important;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Anexos", accept_multiple_files=True)

    # minio_client.put_object(
    #     bucket_name="meu-bucket",
    #     object_name=nome_minio,
    #     data=uploaded_file,
    #     length=len(uploaded_file.read())
    # )
    
    #########################
        
    # Criar espaço vazio nas laterais e centralizar os botões
    esp1, centro, esp2 = st.columns([1, 2, 1])

    with centro:
        # Duas colunas de mesma largura para os botões
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Voltar ao Menu", use_container_width=True):
                st.session_state.pagina = "menu"
                st.rerun()
                st.stop() 
                
        with col2:
            ############################################
            
            if st.button("💾 Salvar", use_container_width=True):

                if numero and tipo and justificativa and data_selecionada and uploaded_files:

                    # 1) Salva o registro no Supabase
                    res = inserir_registro_manual(
                        numero=numero,
                        tipo=tipo,
                        justificativa=justificativa,
                        data_selecionada=data_selecionada,
                        usuario=st.session_state.get("user_name", "desconhecido")
                    )
                    novo_id = res.data[0]["ID"]

                    # 2) Upload dos anexos
                    anexos_nomes = []

                    for idx, file in enumerate(uploaded_files, start=1):
                        ext = file.name.split(".")[-1]
                        nome_minio = f"{novo_id}_{idx}.{ext}"

                        # Salvar temporariamente o arquivo
                        with tempfile.NamedTemporaryFile(delete=False) as tmp:
                            tmp.write(file.getvalue())
                            temp_path = tmp.name  # caminho do arquivo salvo

                        # Enviar ao MinIO
                        meu_minio.upload(
                            object_name="ExpurgosOP/"+ nome_minio,
                            bucket_name="formularios",
                            file_path=temp_path
                        )

                        anexos_nomes.append(nome_minio)

                        # Remove o arquivo temporário
                        os.remove(temp_path)

                    # Opcional, salvar a lista de anexos no Supabase
                    # supabase.table("ExpurgoOP").update({"anexos": anexos_nomes}).eq("id", novo_id).execute()

                    st.session_state.pagina = "Sucesso"
                    st.rerun()
                    st.stop()
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios, inclusive anexos.")

                #st.rerun()
                #st.stop()

# --- PÁGINA CADASTRAR EM MASSA---
if st.session_state.pagina == "CadastrarEmMassa":
    st.markdown(
    "<h1 style='text-align: center; color: #EDEBE6; text-shadow: 1px 1px 3px black;'>"
    "📝 Expurgo OP"
    "</h1>",
    unsafe_allow_html=True
)
    
    ############################################

    st.markdown(
    "<h1 style='text-align: center; color: #EDEBE6; text-shadow: 1px 1px 3px black;'>"
    "Inserir registro em massa"
    "</h1>",
    unsafe_allow_html=True
    )
    
    st.markdown(
    """
    <style>
    div.stDownloadButton > button {
        color: black;              /* cor do texto */
        background-color: #1f77b4; /* fundo do botão */
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
        
    modelo_excel = gerar_modelo_excel()
    st.download_button(
        label="📥 Baixar modelo Excel",
        data=modelo_excel,
        file_name="modelo_documentos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_modelo"
    )
    
    tipo_massa = st.selectbox("Tipo do documento", ["OEF", "OF", "SEFAZ NOTA", "SEFAZ CTE"], key="tipo_massa")
    #anexo_massa = st.file_uploader("Anexo", type=["pdf", "docx", "xlsx", "jpg", "png"], key="anexo_massa")
    arquivo_excel = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"], key="excel_massa")
    
    st.markdown("""
        <style>
        /* Texto do label do file_uploader */
        div[data-testid="stFileUploader"] div {
            color: #EDEBE6 !important;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Anexos", accept_multiple_files=True)

    ###########################################
    ###########################################
    
    if arquivo_excel:
        try:
            df_excel = pd.read_excel(arquivo_excel)
            colunas_esperadas = ["Data", "Numero do documento", "Justificativa"]
            st.dataframe(df_excel)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
        
    # Criar espaço vazio nas laterais e centralizar os botões
    esp1, centro, esp2 = st.columns([1, 2, 1])

    with centro:
        # Duas colunas de mesma largura para os botões
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Voltar ao Menu", use_container_width=True):
                st.session_state.pagina = "menu"
                st.rerun()
                st.stop() 

        with col2:
            ############################################       
            if st.button("💾 Salvar", use_container_width=True): 
                              
                if list(df_excel.columns) != colunas_esperadas:
                    st.error(f"❌ As colunas do arquivo não estão corretas. Esperado: {colunas_esperadas}")
                elif df_excel.isnull().any().any():
                    st.error("⚠️ O arquivo contém campos vazios. Preencha todos antes de enviar.")
                elif not tipo_massa or not uploaded_files:
                    st.error("⚠️ Selecione o Tipo do documento e envie o Anexo antes de salvar.")
                elif not pd.api.types.is_numeric_dtype(df_excel["Numero do documento"]):
                    st.error("⚠️ O campo Numero do documento possui caracteres invalidos. Preencha apenas com números, antes de enviar.")
                else:                       
                    res = inserir_registro_em_massa(df_excel, tipo_massa, usuario=st.session_state.get("user_name", "desconhecido"))

                    # Lista de IDs retornados
                    ids_criados = [item["ID"] for item in res.data]

                    # Upload para cada ID criado
                    for id_registro in ids_criados:

                        for idx, file in enumerate(uploaded_files, start=1):
                            ext = file.name.split(".")[-1]
                            nome_minio = f"{id_registro}_{idx}.{ext}"

                            # Salvar temporariamente o arquivo
                            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                                tmp.write(file.getvalue())
                                temp_path = tmp.name

                            # Upload
                            meu_minio.upload(
                                object_name="ExpurgosOP/"+ nome_minio,
                                bucket_name="formularios",
                                file_path=temp_path
                            )

                            os.remove(temp_path)  # remover arquivo temporário                   
                    
                    st.session_state.pagina = "Sucesso"  # vai pra página oculta   
                                    
                        #st.session_state.pagina = "Sucesso"  # vai pra página oculta

                st.rerun()
                st.stop() 
                        
            ######################################################################################## 

# --- PÁGINA EDITAR ---
elif st.session_state.pagina == "Editar":
    st.markdown(
    "<h1 style='text-align: center; color: #EDEBE6; text-shadow: 1px 1px 3px black;'>"
    "✏️ Editar"
    "</h1>",
    unsafe_allow_html=True
)
    st.markdown("<h3 style='color: white;'>Lista de Registros</h3>", unsafe_allow_html=True)
    df = carregar_dados()
    
    # estilo abrangente para títulos de expander (várias versões do Streamlit)
    st.markdown("""
    <style>
    /* seletor moderno: expander com data-testid */
    div[data-testid="stExpander"] > div[role="button"],
    div[data-testid="stExpander"] > button,
    div[data-testid="stExpander"] summary {
        color: #EDEBE6 !important;
    }
    
    /* spans/labels dentro do botão (algumas builds usam span) */
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] [aria-expanded="true"] span {
        color: #FF8C00 !important;
    }

    /* ícone SVG do expander (setinha) */
    div[data-testid="stExpander"] svg,
    div[data-testid="stExpander"] button svg {
        fill: #EDEBE6 !important;
        stroke: #EDEBE6 !important;
    }

    /* fallback para classes antigas / alternadas */
    .st-expanderHeader,
    .stExpanderHeader,
    .css-1v0mbdj-summary { /* exemplo de classe gerada dinamicamente */
        color: #EDEBE6 !important;
    }

    /* força também quando o texto está dentro de um label/button com background */
    div[data-testid="stExpander"] button {
        color: #EDEBE6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if not df.empty:
        # 🔍 Filtros

        with st.expander("🔎 Filtros"):
            col1, col2 = st.columns(2)

            with col1:
                filtro_tipo_doc = st.selectbox(
                    "Tipo de Documento", 
                    ["Todas"] + sorted(df["TIPO_DOC"].unique().tolist())
                )

            with col2:
                filtro_numero_doc = st.selectbox(
                    "Número do Documento", 
                    ["Todas"] + sorted(df["NUMERO_DOC"].unique().tolist())
                )

            # Filtro de data
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input("Data Mínima", value=None)
            with col2:
                data_fim = st.date_input("Data Máxima", value=None)

        # Aplicar filtros
        if filtro_tipo_doc != "Todas":
            df = df[df["TIPO_DOC"] == filtro_tipo_doc]

        if filtro_numero_doc != "Todas":
            df = df[df["NUMERO_DOC"] == filtro_numero_doc]

        if data_inicio:
            df = df[pd.to_datetime(df["DATA"]) >= pd.to_datetime(data_inicio)]
        if data_fim:
            df = df[pd.to_datetime(df["DATA"]) <= pd.to_datetime(data_fim)]

        # Mostrar tabela filtrada
        #df.drop(columns=['CREATED_AT'], inplace=True)
        df.sort_values(by=["ID", "NUMERO_DOC", "TIPO_DOC", "JUSTIFICATIVA", "DATA"], ascending=[False, False, True, True, True], inplace=True)
        st.dataframe(df.copy().set_index('ID'))

    if not df.empty:

        # Selecionar registro para editar/excluir
        id_registro = st.selectbox("Selecione o ID para editar/excluir", df["ID"].sort_values(ascending=False))

        registro = df[df["ID"] == id_registro].iloc[0]
        
        prefixo = f"ExpurgosOP/{id_registro}"
        
        anexos = meu_minio.listar_anexos("formularios", prefixo)
        
        st.subheader("📎 Anexos deste registro")

        if anexos:
            for caminho_completo in anexos:
                nome = caminho_completo.split("/")[-1]  # extraindo só "123_1.pdf"

                st.write("➡️", nome)

                data = meu_minio.manager.client.get_object(
                    "formularios",
                    caminho_completo
                ).read()

                st.markdown(
                """
                <style>
                div.stDownloadButton > button {
                    color: black;              /* cor do texto */
                    background-color: #1f77b4; /* fundo do botão */
                    border-radius: 8px;
                    font-weight: bold;
                }
                </style>
                """,
                unsafe_allow_html=True
                )

                st.download_button("Baixar", data, file_name=nome)
        else:
            st.info("Nenhum anexo encontrado para este registro.")
            
        with st.expander("✏️ Editar Registro"):
            opcoes_tipo_documento = ["OEF", "OF", "SEFAZ NOTA", "SEFAZ CTE"]
                        
            novo_tipo_documento = st.selectbox(
                "Tipo de Documento",
                options=opcoes_tipo_documento,
                index=opcoes_tipo_documento.index(registro["TIPO_DOC"]) 
                    if registro["TIPO_DOC"] in opcoes_tipo_documento else 0
            )
            
            novo_numero_doc = st.text_input("Numero do Documento", registro["NUMERO_DOC"])
            
            novo_justificativa = st.text_input("Justificativa", registro["JUSTIFICATIVA"])
        
            novo_data = st.date_input(
                "Data",
                value=(pd.to_datetime(registro["DATA"]).date()
                    if pd.notna(registro["DATA"])
                    else None)
            )

            st.markdown(
            """
            <style>
            div.stDownloadButton > button {
                color: black;              /* cor do texto */
                background-color: #FF8C00; /* fundo do botão */
                border-radius: 8px;
                font-weight: bold;
            }
            </style>
            """,
            unsafe_allow_html=True
            )

            if st.button("Salvar Alterações"):
                existe = verificar_existencia(
                    novo_numero_doc,
                    novo_tipo_documento,
                    novo_justificativa,
                    novo_data
                )

                if existe:                    
                    st.error("❌ Este cadastro já existe.")
                else:
                    #st.info("🔄 Atualizando registro...")
                    atualizar_registro(id_registro, novo_numero_doc, novo_tipo_documento, novo_justificativa, novo_data)
                    st.session_state.pagina = "Editado"  # vai pra página oculta
                    st.rerun()
                    st.stop() 
                    
        # Inicializar flag
        if "confirmar_exclusao" not in st.session_state:
            st.session_state.confirmar_exclusao = False
        if "registro_pendente_exclusao" not in st.session_state:
            st.session_state.registro_pendente_exclusao = None

        with st.expander("🗑️ Excluir Registro"):

            # Primeiro botão: pedir confirmação
            if st.button("Excluir", type="primary"):
                st.session_state.confirmar_exclusao = True
                st.session_state.registro_pendente_exclusao = id_registro
                st.rerun()

            # Se clicou em "Excluir", aparece a confirmação
            if st.session_state.confirmar_exclusao:

                st.warning("⚠️ Tem certeza de que deseja excluir este registro?")

                col1, col2 = st.columns(2)

                # Botão "Sim"
                with col1:
                    if st.button("Sim, excluir", type="primary"):
                        excluir_registro(st.session_state.registro_pendente_exclusao)
                        st.session_state.confirmar_exclusao = False
                        st.session_state.registro_pendente_exclusao = None
                        st.session_state.pagina = "Excluido"
                        st.rerun()

                # Botão "Não"
                with col2:
                    if st.button("Cancelar"):
                        st.session_state.confirmar_exclusao = False
                        st.session_state.registro_pendente_exclusao = None
                        st.rerun()
    else:
        st.info("Nenhum registro encontrado.")

    # Criar espaço vazio nas laterais e centralizar os botões
    esp1, centro, esp2 = st.columns([1, 1, 1])

    with centro:
        if st.button("Voltar ao Menu", use_container_width=True):
            st.session_state.pagina = "menu"
            st.rerun()
            st.stop()   # ← ESSENCIAL NO LUGAR DO return            

# 🟢 Página oculta de sucesso (não aparece no menu)
elif st.session_state.pagina == "Sucesso":

    # Força a página a subir para o topo
    st.markdown("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="foguete">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>🎈 Cadastro efetuado!</h3>", unsafe_allow_html=True)

    fox_image_html = f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    ">
        <img src="{fox_image}" alt="Foxy" 
            style="
                width: min(400px, 80vw);
                height: auto;
                margin-bottom: 10px;
            ">
    </div>
    """
    
    st.markdown(fox_image_html, unsafe_allow_html=True)
    st.success("✅ Registro atualizado com sucesso!")
    st.balloons()
    
    # Criar espaço vazio nas laterais e centralizar os botões
    esp1, centro, esp2 = st.columns([1, 1, 1])

    with centro:
        if st.button("Ok", use_container_width=True):
            st.session_state.pagina = "menu"
            st.rerun()
            st.stop()   # ← ESSENCIAL NO LUGAR DO return     

# 🟢 Página oculta de editado (não aparece no menu)
elif st.session_state.pagina == "Editado":

    # Força a página a subir para o topo
    st.markdown("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="foguete">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>🎈 Dado editado!</h3>", unsafe_allow_html=True)

    fox_image_html = f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    ">
        <img src="{fox_image}" alt="Foxy" 
            style="
                width: min(400px, 80vw);
                height: auto;
                margin-bottom: 10px;
            ">
    </div>
    """

    st.markdown(fox_image_html, unsafe_allow_html=True)

    st.success("✅ Registro atualizado com sucesso!")
    st.balloons()

    # Criar espaço vazio nas laterais e centralizar os botões
    esp1, centro, esp2 = st.columns([1, 1, 1])

    with centro:
        if st.button("Ok", use_container_width=True):
            st.session_state.pagina = "menu"
            st.rerun()
            st.stop()   # ← ESSENCIAL NO LUGAR DO return   
    
# 🟢 Página oculta de editado (não aparece no menu)
elif st.session_state.pagina == "Excluido":

    # Força a página a subir para o topo
    st.markdown("""
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="foguete">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>🎈 Dado excluído!</h3>", unsafe_allow_html=True)

    fox_image_html = f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    ">
        <img src="{fox_image}" alt="Foxy" 
            style="
                width: min(400px, 80vw);
                height: auto;
                margin-bottom: 10px;
            ">
    </div>
    """

    st.markdown(fox_image_html, unsafe_allow_html=True)

    st.success("✅ Registro excluído com sucesso!")
    st.balloons()

    # Criar espaço vazio nas laterais e centralizar os botões
    esp1, centro, esp2 = st.columns([1, 1, 1])

    with centro:
        if st.button("Ok", use_container_width=True):
            st.session_state.pagina = "menu"
            st.rerun()
            st.stop()   # ← ESSENCIAL NO LUGAR DO return   
