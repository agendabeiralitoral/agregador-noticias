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

# --- MELHORIAS DE DESIGN E CABEÇALHO FIXO (CSS) ---
st.markdown(
    """
    <style>
    /* Estilo global */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Cabeçalho Fixo no Topo */
    .sticky-header {
        position: sticky;
        top: 0;
        background-color: #f8f9fa;
        z-index: 99999;
        padding-top: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Título Principal no Cabeçalho */
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0;
        letter-spacing: -0.5px;
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
    
    /* Botão minimalista apenas com o logotipo do Facebook */
    .fb-icon-btn {
        background-color: #1877F2;
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: background-color 0.2s ease, transform 0.2s ease;
    }
    .fb-icon-btn:hover {
        background-color: #166fe5;
        color: white;
        transform: scale(1.05);
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


# --- RECOLHA AUTOMÁTICA DE TODAS AS FONTES ---
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

# --- CABEÇALHO FIXO COM TEXTO NA PÁGINA PRINCIPAL ---
st.markdown('<div class="sticky-header">', unsafe_allow_html=True)

col_title, col_info = st.columns([2, 2])
with col_title:
    st.markdown(
        '<h1 class="header-title">Agenda Beira Litoral</h1>',
        unsafe_allow_html=True,
    )

with col_info:
    st.markdown(
        f"<div style='text-align: right; padding-top: 10px; font-size: 0.95rem; color: #475569;'>"
        f"Concelho: <b>{municipio_selecionado}</b> | Categoria: <b>{categoria_selecionada}</b><br>"
        f"Fontes ativas: <b>{len(st.session_state.fontes_regionais)}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# --- CORPO DA PÁGINA (LISTA DE NOTÍCIAS QUE FAZ SCROLL) ---
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

    # Renderização dos cartões de notícias com hashtag integrada no partilhar
    for entrada in noticias_finais[:limite]:
        titulo = entrada.get("title", "Sem título")
        link = entrada.get("link", "#")
        data = entrada.get("published", "Data indisponível")
        resumo = entrada.get("summary", "Sem resumo disponível.")
        origem = entrada.get("fonte_origem", "Fonte desconhecida")

        # Inclusão da hashtag no URL de partilha do Facebook
        link_encoded = urllib.parse.quote(link)
        hashtag_text = urllib.parse.quote(" #agendabeiralitoral")
        fb_share_url = f"https://www.facebook.com/sharer/sharer.php?u={link_encoded}&quote={hashtag_text}"

        cartao_html = f"""
        <div class="news-card">
            <div class="news-title">{titulo}</div>
            <div class="news-meta">📰 <b>{origem}</b> &nbsp;|&nbsp; 📅 {data}</div>
            <div style="color: #475569; font-size: 0.95rem; margin-bottom: 15px;">{resumo}</div>
            <div style="display: flex; gap: 20px; align-items: center;">
                <a href="{link}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 600; font-size: 0.9rem;">🔗 Ler Artigo Completo</a>
                <a href="{fb_share_url}" target="_blank" class="fb-icon-btn" title="Partilhar no Facebook">f</a>
            </div>
        </div>
        """
        st.markdown(cartao_html, unsafe_allow_html=True)
else:
    st.warning("Não foi possível carregar notícias de nenhuma das fontes ativas.")