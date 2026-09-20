import urllib.parse
import feedparser
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Agregador Cultural e Municipal", page_icon="🗺️", layout="wide"
)

st.title("🗺️ Agregador de Notícias Municipais, Cultura e Eventos")
st.write(
    "Filtre a atualidade por concelho e categoria, com gestão dinâmica de fontes RSS."
)

# 1. Lista de Municípios
municipios = [
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
st.sidebar.header("⚙️ Configurações e Filtros")

with st.sidebar.expander("➕ Adicionar Nova Fonte RSS"):
    novo_nome = st.text_input("Nome da Fonte (ex: Jornal Local)")
    novo_url = st.text_input("URL do Feed RSS (ex: https://...)")

    if st.button("Guardar Fonte"):
        if novo_nome and novo_url:
            st.session_state.fontes_regionais[novo_nome] = novo_url
            st.success(f"Fonte '{novo_nome}' adicionada com sucesso!")
        else:
            st.warning("Por favor, preencha o nome e o URL.")

st.sidebar.markdown("---")
st.sidebar.header("Filtros de Pesquisa")

municipio_selecionado = st.sidebar.selectbox(
    "1. Escolha o Concelho:", sorted(municipios)
)
categoria_selecionada = st.sidebar.selectbox(
    "2. Escolha a Categoria:", ["Todas"] + sorted(list(categorias_keywords.keys()))
)

fonte_escolhida = st.sidebar.selectbox(
    "Fonte de Notícias:", list(st.session_state.fontes_regionais.keys())
)
url_rss = st.session_state.fontes_regionais[fonte_escolhida]
limite = st.sidebar.slider("Número máximo de notícias:", 3, 20, 5)


@st.cache_data(ttl=600)
def carregar_rss(url):
    return feedparser.parse(url)


feed = carregar_rss(url_rss)

# --- CORPO DA PÁGINA ---
st.subheader(
    f"Resultados para: {municipio_selecionado} | Categoria: {categoria_selecionada}"
)
st.markdown(f"_**Fonte ativa:** {fonte_escolhida} (`{url_rss}`)_")
st.markdown("---")

if feed.entries:
    filtrados_municipio = [
        entry
        for entry in feed.entries
        if municipio_selecionado.lower() in entry.get("title", "").lower()
        or municipio_selecionado.lower() in entry.get("summary", "").lower()
    ]

    base_noticias = (
        filtrados_municipio if filtrados_municipio else feed.entries
    )

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
            f"Não foram encontradas notícias específicas para **{municipio_selecionado}** na categoria **{categoria_selecionada}**."
        )
        noticias_finais = feed.entries[:limite]
    else:
        st.success(
            f"Encontradas {len(noticias_finais)} notícias correspondentes."
        )

    for entrada in noticias_finais[:limite]:
        titulo = entrada.get("title", "Sem título")
        link = entrada.get("link", "#")
        data = entrada.get("published", "Data indisponível")
        resumo = entrada.get("summary", "Sem resumo disponível.")

        with st.container():
            st.subheader(titulo)
            st.caption(f"📅 Publicado a: {data}")
            st.write(resumo, unsafe_allow_html=True)

            link_encoded = urllib.parse.quote(link)
            fb_share_url = f"https://www.facebook.com/sharer/sharer.php?u={link_encoded}"

            col1, col2, _ = st.columns([2, 2, 6])
            with col1:
                st.markdown(f"[🔗 Ler Artigo Completo]({link})")
            with col2:
                st.markdown(
                    f'<a href="{fb_share_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#1877F2; color:white; border:none; padding:8px 16px; border-radius:4px; font-weight:bold; cursor:pointer;">📘 Partilhar no Facebook</button></a>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
else:
    st.warning(
        "Não foi possível estabelecer ligação à fonte de notícias selecionada ou o feed está vazio."
    )