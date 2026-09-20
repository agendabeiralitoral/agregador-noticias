import urllib.parse
import feedparser
import streamlit as st

# Configuração da página e layout
st.set_page_config(
    page_title="Agenda Beira Litoral",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- MELHORIAS DE DESIGN (CSS CUSTOMIZADO) ---
st.markdown(
    """
    <style>
    /* Estilo global e fontes */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Cartões de notícias modernos */
    .news-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .news-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #cbd5e1;
    }
    
    /* Títulos dos artigos */
    .news-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    /* Metadados */
    .news-meta {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 12px;
    }
    
    /* Botão personalizado do Facebook */
    .fb-btn {
        background-color: #1877F2;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: none;
        cursor: pointer;
    }
    .fb-btn:hover {
        background-color: #166fe5;
        color: white;
    }
    
    /* Ajustes na barra lateral */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- LOGOTIPO NO TOPO ---
col_logo1, col_logo2, col_logo3 = st.columns([1, 4, 1])
with col_logo2:
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        st.title("agenda beiralitoral")
        st.warning(
            "⚠️ Coloque a imagem do logotipo com o nome 'logo.png' na pasta do repositório."
        )

st.markdown("<br>", unsafe_allow_html=True)

# 1. Lista base de Municípios
municipios_lista = [
    "Águeda",
    "Albergaria-a-Velha",
    "Alvaiázere",
    "Anadia",
    "Ansião",
    "Arganil",
    "Aveiro",
    "Batalha",
    "Cantanhede",
    "Castanheira de Pera",
    "Coimbra",
    "Condeixa-a-Nova",
    "Estarreja",
    "Figueira da Foz",
    "Figueiró dos Vinhos",
    "Góis",
    "Ílhavo",
    "Leiria",
    "Lousã",
    "Mealhada",
    "Mira",
    "Miranda do Corvo",
    "Montemor-o-Velho",
    "Murtosa",
    "Oliveira de Azeméis",
    "Oliveira do Bairro",
    "Ourém",
    "Ovar",
    "Pedrógão Grande",
    "Penacova",
    "Penela",
    "Pombal",
    "São João da Madeira",
    "Sever do Vouga",
    "Soure",
    "Vagos",
    "Vale de Cambra",
    "Vila Nova de Poiares",
]

municipios = ["Todos"] + sorted(municipios_lista)

# 2. Categorias e palavras-chave associadas
categorias_keywords = {
    "Cinema e Vídeo": ["cinema", "filme", "filmes", "vídeo", "curta-metragem"],
    "Conferências": ["conferência", "colóquio", "debate", "fórum", "seminário"],
    "Desporto": [
        "futebol",
        "desporto",
        "corrida",
        "clube",
        "campeonato",
        "jogo",
    ],
    "Encontros": ["encontro", "reunião", "congresso", "jornadas"],
    "Exposições": ["exposição", "museu", "galeria", "mostra"],
    "Feiras e Mercados": ["feira", "mercado", "mercado municipal", "certame"],
    "Festas Populares": ["festa popular", "festas populares", "tasquinhas"],
    "Festas Religiosas": ["festa religiosa", "procissão", "padroeiro", "igreja"],
    "Gastronomia": [
        "gastronomia",
        "culinária",
        "prato típico",
        "vinho",
        "restaurante",
    ],
    "Infantil": ["infantil", "crianças", "miúdos", "famílias"],
    "Literatura": ["livro", "literatura", "escritor", "apresentação de livro"],
    "Música": ["concerto", "música", "banda", "festival", "espetáculo musical"],
    "Natureza e Passeios": [
        "natureza",
        "trilho",
        "percurso pedestre",
        "passeio",
        "serra",
        "rio",
    ],
    "Romarias": ["romaria", "santuário"],
    "Teatro e Dança": ["teatro", "dança", "espetáculo", "peça de teatro"],
    "Tradições e Cultura": [
        "tradição",
        "cultura",
        "etnografia",
        "património",
        "história",
    ],
}

# --- GESTÃO DE ESTADO PARA AS FONTES RSS ---
if "fontes_regionais" not in st.session_state:
    st.session_state.fontes_regionais = {
        "Notícias de Coimbra / Regional": "https://www.noticiasdecoimbra.pt/feed/",
        "Diário As Beiras": "https://asbeiras.pt/feed/",
        "RTP Centro": "https://www.rtp.pt/noticias/rss/pais/centro",
    }

# --- BARRA LATERAL ---
st.sidebar.markdown(
    "### 🎛️ Painel de Controlo", help="Filtros e Gestão de Fontes"
)

# 1. Secção para CONSULTAR e GERIR as fontes configuradas
with st.sidebar.expander("📋 Fontes RSS Configuradas"):
    if st.session_state.fontes_regionais:
        for nome, url in list(st.session_state.fontes_regionais.items()):
            st.markdown(f"**{nome}**")
            st.code(url, language="text")
            if st.button(f"🗑️ Remover '{nome}'", key=f"btn_rem_{nome}"):
                del st.session_state.fontes_regionais[nome]
                st.rerun()
            st.markdown("---")
    else:
        st.info("Não existem fontes configuradas.")

# 2. Secção para ADICIONAR nova fonte RSS
with st.sidebar.expander("➕ Adicionar Nova Fonte RSS"):
    novo_nome = st.text_input("Nome da Fonte (ex: Jornal Local)")
    novo_url = st.text_input("URL do Feed RSS (ex: https://...)")

    if st.button("Guardar Nova Fonte"):
        if novo_nome and novo_url:
            st.session_state.fontes_regionais[novo_nome] = novo_url
            st.success(f"Fonte '{novo_nome}' adicionada com sucesso!")
            st.rerun()
        else:
            st.warning("Por favor, preencha o nome e o URL.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros de Pesquisa")

municipio_selecionado = st.sidebar.selectbox(
    "Escolha o Concelho:", municipios
)
categoria_selecionada = st.sidebar.selectbox(
    "Escolha a Categoria:", ["Todas"] + sorted(list(categorias_keywords.keys()))
)
limite = st.sidebar.slider("Número máximo de notícias a exibir:", 3, 30, 10)


@st.cache_data(ttl=600)
def carregar_rss(url):
    return feedparser.parse(url)


# --- RECOLHA AUTOMÁTICA DE TODAS AS FONTES (COM PROTEÇÃO) ---
todas_as_noticias = []
for nome_fonte, url_fonte in st.session_state.fontes_regionais.items():
    try:
        feed = carregar_rss(url_fonte)
        if feed and hasattr(feed, "entries"):
            for entrada in feed.entries:
                entrada["fonte_origem"] = nome_fonte
                todas_as_noticias.append(entrada)
    except Exception:
        continue

# --- CORPO DA PÁGINA ---
col_info1, col_info2 = st.columns([3, 1])
with col_info1:
    st.markdown(
        f"#### Filtro ativo: <span style='color:#2563eb;'>{municipio_selecionado}</span> | Categoria: <span style='color:#2563eb;'>{categoria_selecionada}</span>",
        unsafe_allow_html=True,
    )
with col_info2:
    st.markdown(
        f"<div style='text-align: right; color: #64748b; font-size: 0.9rem;'>Fontes ativas: <b>{len(st.session_state.fontes_regionais)}</b></div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

if todas_as_noticias:
    if municipio_selecionado == "Todos":
        base_noticias = todas_as_noticias
    else:
        base_noticias = [
            entry
            for entry in todas_as_noticias
            if municipio_selecionado.lower() in entry.get("title", "").lower()
            or municipio_selecionado.lower() in entry.get("summary", "").lower()
        ]

    if categoria_selecionada != "Todas":
        palavras_chave = categorias_keywords[categoria_selecionada]
        noticias_finais = []
        for entry in base_noticias:
            texto_completo = (
                entry.get("title", "") + " " + entry.get("summary", "")
            ).lower()
            if any(kw in texto_completo for kw in palavras_chave):
                noticias_finais.append(entry)
    else:
        noticias_finais = base_noticias

    if not noticias_finais:
        st.info(
            f"Não foram encontradas notícias para **{municipio_selecionado}** na categoria **{categoria_selecionada}** nas fontes atuais."
        )
        noticias_finais = todas_as_noticias[:limite]
    else:
        st.success(
            f"Encontradas {len(noticias_finais)} notícias correspondentes."
        )

    # Renderização limpa em formato de cartões modernos
    for entrada in noticias_finais[:limite]:
        titulo = entrada.get("title", "Sem título")
        link = entrada.get("link", "#")
        data = entrada.get("published", "Data indisponível")
        resumo = entrada.get("summary", "Sem resumo disponível.")
        origem = entrada.get("fonte_origem", "Fonte desconhecida")

        link_encoded = urllib.parse.quote(link)
        fb_share_url = f"https://www.facebook.com/sharer/sharer.php?u={link_encoded}"

        # HTML estruturado para cada cartão de notícia
        cartao_html = f"""
        <div class="news-card">
            <div class="news-title">{titulo}</div>
            <div class="news-meta">📰 <b>{origem}</b> &nbsp;|&nbsp; 📅 {data}</div>
            <div style="color: #475569; font-size: 0.95rem; margin-bottom: 15px;">{resumo}</div>
            <div style="display: flex; gap: 15px; align-items: center;">
                <a href="{link}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 600; font-size: 0.9rem;">🔗 Ler Artigo Completo</a>
                <a href="{fb_share_url}" target="_blank" class="fb-btn">📘 Partilhar no Facebook</a>
            </div>
        </div>
        """
        st.markdown(cartao_html, unsafe_allow_html=True)
else:
    st.warning("Não foi possível carregar notícias de nenhuma das fontes ativas.")