import streamlit as st
import pandas as pd
import sqlite3
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors
from uuid import uuid4
import tempfile
import pytesseract
from PIL import Image

# Configurar o caminho do Tesseract
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:  # Heroku/Linux
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'  # Tesseract estará no PATH no Heroku

# Inicializar o estado da sessão para armazenar dados do usuário e jogadores selecionados
if 'dados_usuario' not in st.session_state:
    st.session_state['dados_usuario'] = None
if 'jogadores_selecionados' not in st.session_state:
    st.session_state['jogadores_selecionados'] = []

# Conexão com SQLite
conn = sqlite3.connect('fan_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
    ID TEXT PRIMARY KEY,
    NOME TEXT,
    CPF TEXT,
    ENDERECO TEXT,
    EMAIL TEXT,
    JOGADORES TEXT,
    JOGOS TEXT,
    EVENTOS TEXT,
    COMPRAS TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS twitter_data (
    ID TEXT PRIMARY KEY,
    TWITTER_USERNAME TEXT,
    FOLLOWING TEXT,
    INTERACOES TEXT
)''')
conn.commit()
conn.close()

# Configuração da página
st.set_page_config(page_title="Know Your Fan - FURIA", page_icon="https://cdn.dribbble.com/userupload/11627401/file/original-405f194bea083344029e99856c00f6f8.png?resize=1024x768&vertical=center", layout="wide")

st.markdown(
    """
    <style>
    /* Definir a imagem de fundo para o corpo da página */
    .stApp {
        background: url("https://pbs.twimg.com/media/F98rmOiWYAAFMyD?format=jpg&name=large");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white; /* Texto branco para contraste */
    }

    /* Adicionar um fundo preto opaco para os elementos do formulário */
    .stTextInput, .stSelectbox, .stTextArea, .stButton, .stForm {
        background-color: rgb(0, 0, 0); /* Fundo preto opaco */
        padding: 10px;
        border-radius: 5px;
    }

    /* Manter fundo semi-transparente para outras seções */
    .stMarkdown, .stFileUploader,st.multiselect, .stSuccess, .stInfo {
        background-color: rgba(0, 0, 0, 0.7); /* Fundo preto semi-transparente */
        padding: 10px;
        border-radius: 5px;
    }

    /* Garantir que os cabeçalhos também sejam brancos */
    h1, h2, h3, h4, h5, h6 {
        color: white;
    }

    /* Ajustar a cor do texto dentro dos contêineres */
    .stMarkdown p, .stMarkdown div, .stTextInput input, .stTextArea textarea, .stSelectbox div, .stButton button {
        color: white;
    }

    /* Ajustar bordas dos contêineres para melhor contraste */
    .stContainer {
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Função para coletar dados do usuário
def coletar_dados_usuario():
    st.header("🔥Queremos conhecer você!")
    st.write("Preencha os dados abaixo para que possamos personalizar sua experiência como FURIOSO.")
    with st.form("form_usuario"):
        nome = st.text_input("Nome completo")
        cpf = st.text_input("CPF")
        endereco = st.text_input("Endereço")
        email = st.text_input("E-mail")
        jogadores_favoritos = st.multiselect(
            "Jogadores preferidos (elenco atual de CS da FURIA)",
            ["FalleN", "yuurih", "KSCERATO", "chelo", "skullz", "guerri (coach)"]
        )
        jogos_favoritos = st.multiselect("Jogos favoritos", ["CS:GO", "Valorant", "League of Legends", "Outros"])
        eventos_ano = st.text_area("Quais eventos de esports que participou no último ano?")
        compras_ano = st.text_area("Quais produtos da FURIA você adquiriu recentemente?")
        submitted = st.form_submit_button("Enviar")
        if submitted:
            user_id = str(uuid4())
            conn = sqlite3.connect('fan_data.db')
            dados = pd.DataFrame({
                'ID': [user_id],
                'NOME': [nome],
                'CPF': [cpf],
                'ENDERECO': [endereco],
                'EMAIL': [email],
                'JOGADORES': [','.join(jogadores_favoritos)],
                'JOGOS': [','.join(jogos_favoritos)],
                'EVENTOS': [eventos_ano],
                'COMPRAS': [compras_ano]
            })
            dados.to_sql('usuarios', conn, if_exists='append', index=False)
            conn.close()
            # Armazenar os dados no estado da sessão
            st.session_state['dados_usuario'] = dados
            st.session_state['jogadores_selecionados'] = jogadores_favoritos
            st.success("Dados salvos com sucesso!")
    return st.session_state['dados_usuario'], st.session_state['jogadores_selecionados']

# Função para validar documentos usando pytesseract
def validar_documento(imagem_path):
    try:
        image = Image.open(imagem_path)
        texto = pytesseract.image_to_string(image, lang='eng')
        if texto:
            digits = ''.join([c for c in texto if c.isdigit()])
            if len(digits) >= 11:
                return True, texto
            return False, "Documento inválido: número de CPF não encontrado"
        return False, "Nenhum texto detectado"
    except Exception as e:
        return False, f"Erro ao processar a imagem: {str(e)}"

# Função para coletar dados do Twitter/X (simulada devido ao plano gratuito)
def coletar_dados_twitter(username):
    following = ["FURIA", "LOUD", "TeamLiquid"]
    interacoes = ["Assisti ao Major CS:GO 2024! #FURIA", "Jogando Valorant hoje! #esports"]
    return {"following": following, "interacoes": interacoes}

# Dados fictícios de experiências
experiencias = pd.DataFrame({
    'EXPERIENCIA': [
        'PGL Astana 2025',
        'IEM Dallas 2025',
        'BLAST Austin Major 2025',
        'Camiseta ULTRAS',
        'Camiseta FURIA x Adidas',
        'Jersey FURIA 2025',
        'Workshop Valorant',
        'Conteúdo Exclusivo FURIA - Bastidores CS:GO'
    ],
    'TIPO': [
        'Evento',
        'Evento',
        'Evento',
        'Produto',
        'Produto',
        'Produto',
        'Workshop',
        'Conteúdo'
    ],
    'JOGO': [
        'CS:GO',
        'CS:GO',
        'CS:GO',
        'Geral',
        'Geral',
        'Geral',
        'Valorant',
        'CS:GO'
    ],
    'TIME': [
        'FURIA',
        'FURIA',
        'FURIA',
        'FURIA',
        'FURIA',
        'FURIA',
        'Nenhum',
        'FURIA'
    ],
    'FEATURE1': [1, 1, 1, 0, 0, 0, 0, 0],  # Eventos
    'FEATURE2': [0, 0, 0, 1, 1, 1, 0, 0],  # Produtos
    'FEATURE3': [0, 0, 0, 0, 0, 0, 1, 1]   # Workshops/Conteúdo
})

# Função para recomendar experiências
def recomendar_experiencias(dados_usuario):
    if dados_usuario is None or dados_usuario.empty:
        return pd.DataFrame()

    # Extrair preferências do usuário
    usuario_features = [0, 0, 0]  # [Eventos, Produtos, Workshops/Conteúdo]
    jogos_favoritos = dados_usuario['JOGOS'].iloc[0].split(',') if 'JOGOS' in dados_usuario and dados_usuario['JOGOS'].iloc[0] else []
    jogadores_favoritos = dados_usuario['JOGADORES'].iloc[0].split(',') if 'JOGADORES' in dados_usuario and dados_usuario['JOGADORES'].iloc[0] else []

    # Definir features do usuário
    if 'EVENTOS' in dados_usuario and dados_usuario['EVENTOS'].iloc[0]:
        usuario_features[0] = 1  # Interesse em eventos
    if 'COMPRAS' in dados_usuario and dados_usuario['COMPRAS'].iloc[0]:
        usuario_features[1] = 1  # Interesse em produtos
    if 'Valorant' in jogos_favoritos:
        usuario_features[2] = 1  # Interesse em workshops/conteúdo (Valorant)

    # Ajustar pesos com base nos jogadores favoritos (todos são de CS:GO)
    if jogadores_favoritos:
        usuario_features[0] += 0.5  # Aumentar peso para eventos (todos os jogadores são de CS:GO)
        usuario_features[1] += 0.5  # Aumentar peso para produtos (ex.: camisetas dos jogadores)

    # Filtrar experiências com base nos jogos favoritos
    experiencias_filtradas = experiencias.copy()
    if jogos_favoritos:
        mask = experiencias_filtradas['JOGO'].apply(lambda x: x in jogos_favoritos or x == 'Geral')
        experiencias_filtradas = experiencias_filtradas[mask]

    if experiencias_filtradas.empty:
        experiencias_filtradas = experiencias  # Se não houver correspondência, usar todas as experiências

    # Aplicar KNN para encontrar as experiências mais próximas
    X = experiencias_filtradas[['FEATURE1', 'FEATURE2', 'FEATURE3']].values
    if len(X) == 0:
        return pd.DataFrame()

    knn = NearestNeighbors(n_neighbors=min(3, len(X)), metric='euclidean')
    knn.fit(X)
    distances, indices = knn.kneighbors([usuario_features])

    # Obter recomendações iniciais
    recomendacoes = experiencias_filtradas.iloc[indices[0]][['EXPERIENCIA', 'TIPO', 'JOGO', 'TIME']]

    # Garantir diversidade: tentar incluir pelo menos um evento, um produto e um workshop/conteúdo
    tipos_presentes = recomendacoes['TIPO'].tolist()
    if len(recomendacoes) < 3:
        tipos_desejados = ['Evento', 'Produto', 'Workshop' if 'Workshop' in experiencias_filtradas['TIPO'].values else 'Conteúdo']
        for tipo in tipos_desejados:
            if tipo not in tipos_presentes and len(recomendacoes) < 3:
                # Buscar uma experiência do tipo desejado
                opcoes = experiencias_filtradas[experiencias_filtradas['TIPO'] == tipo]
                if not opcoes.empty:
                    # Adicionar a primeira opção disponível
                    nova_recomendacao = opcoes.iloc[0][['EXPERIENCIA', 'TIPO', 'JOGO', 'TIME']]
                    recomendacoes = pd.concat([recomendacoes, pd.DataFrame([nova_recomendacao])], ignore_index=True)
                    tipos_presentes.append(tipo)

    return recomendacoes.head(3)  # Retornar no máximo 3 recomendações

# Função para sugerir produtos ou redes sociais com base nos jogadores selecionados
def sugerir_produtos_ou_redes(jogadores_selecionados):
    if not jogadores_selecionados:
        return "Nenhum jogador selecionado para sugestões."
    
    redes_sociais = {
        "FalleN": "Twitter: @FalleNCS",
        "yuurih": "Twitter: @yuurih",
        "KSCERATO": "Twitter: @kscerato",
        "chelo": "Twitter: @chelok1ng",
        "skullz": "Twitter: @skullzcs",
        "guerri": "Twitter: @guerri"
    }
    
    sugestoes = []
    for jogador in jogadores_selecionados:
        if len(sugestoes) % 2 == 0:
            sugestoes.append(f"Que tal uma camiseta personalizada do {jogador}? Disponível na loja oficial da FURIA!")
        else:
            sugestoes.append(f"Siga o {jogador} nas redes sociais: {redes_sociais.get(jogador, 'Não disponível')}")
    
    return "\n".join(sugestoes)

# Interface principal
if __name__ == "__main__":
    st.title("Know Your Fan - Protótipo para Fãs da FURIA")
    dados_usuario, jogadores_selecionados = coletar_dados_usuario()

    # Upload de documento
    st.header("Upload de Documento")
    uploaded_file = st.file_uploader("Faça upload do seu documento (ex.: RG, CPF)", type=["jpg", "png"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name
        valido, mensagem = validar_documento(temp_path)
        if valido:
            st.success("Documento válido! Texto extraído: " + mensagem)
        else:
            st.error(mensagem)
        os.remove(temp_path)

    # Vincular Twitter/X
    st.header("Vincular Twitter/X")
    twitter_username = st.text_input("Nome de usuário no Twitter/X (sem @)")
    if st.button("Vincular"):
        dados_twitter = coletar_dados_twitter(twitter_username)
        if "error" not in dados_twitter:
            st.write("Páginas seguidas:", dados_twitter["following"])
            st.write("Interações relevantes:", dados_twitter["interacoes"])
            user_id = str(uuid4())
            conn = sqlite3.connect('fan_data.db')
            pd.DataFrame({
                'ID': [user_id],
                'TWITTER_USERNAME': [twitter_username],
                'FOLLOWING': [','.join(dados_twitter["following"])],
                'INTERACOES': [','.join(dados_twitter["interacoes"])]
            }).to_sql('twitter_data', conn, if_exists='append', index=False)
            conn.close()
            st.success("Dados do Twitter/X salvos! (Dados simulados para demonstração)")
        else:
            st.error(dados_twitter["error"])

    # Recomendações e sugestões (usando o estado da sessão)
    if st.session_state['dados_usuario'] is not None and not st.session_state['dados_usuario'].empty:
        st.header("🎯 Recomendações Personalizadas")
        recomendacoes = recomendar_experiencias(st.session_state['dados_usuario'])
        
        if not recomendacoes.empty:
            st.write("Com base no seu perfil, recomendamos as seguintes experiências:")
            st.divider()
            
            for idx, row in recomendacoes.iterrows():
                with st.container(border=True):
                    st.subheader(f"⭐ {row['EXPERIENCIA']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Tipo:** {row['TIPO']}")
                        st.markdown(f"**Jogo:** {row['JOGO']}")
                    with col2:
                        st.markdown(f"**Time:** {row['TIME']}")
            st.divider()
        else:
            st.info("Preencha os dados para receber recomendações.")
        
        st.header("🛒 Sugestões para Você")
        sugestoes = sugerir_produtos_ou_redes(st.session_state['jogadores_selecionados'])
        st.write(sugestoes)