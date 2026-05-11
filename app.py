import json
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).parent
USERS_FILE = BASE_DIR / "usuarios.json"
HISTORICO_FILE = BASE_DIR / "historico.json"
FEEDBACK_FILE = BASE_DIR / "feedbacks.json"


def ensure_json_file(path: Path, default):
    if not path.exists():
        path.write_text(json.dumps(default, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path, default):
    ensure_json_file(path, default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------- LOGIN ----------------
def load_users():
    return read_json(USERS_FILE, {"magdiel": "1234", "amigo": "1234"})


def check_login(user, password):
    users = load_users()
    return users.get(user.strip().lower()) == password


# ---------------- DADOS DE EXEMPLO ----------------
def get_jogos(campeonato):
    exemplos = {
        "Brasileirão Série A": [
            {"mandante": "Flamengo", "visitante": "Palmeiras", "palpite": "Mais de 8.5 escanteios", "confianca": 62},
            {"mandante": "São Paulo", "visitante": "Cruzeiro", "palpite": "Menos de 5.5 cartões", "confianca": 54},
            {"mandante": "Grêmio", "visitante": "Internacional", "palpite": "Ambas marcam", "confianca": 51},
        ],
        "Brasileirão Série B": [
            {"mandante": "Goiás", "visitante": "Coritiba", "palpite": "Mais de 7.5 escanteios", "confianca": 58},
            {"mandante": "Avaí", "visitante": "Vila Nova", "palpite": "Menos de 3.5 gols", "confianca": 61},
        ],
        "Copa do Brasil": [
            {"mandante": "Fluminense", "visitante": "Bahia", "palpite": "Mais de 8.5 escanteios", "confianca": 59},
            {"mandante": "Athletico-PR", "visitante": "Atlético-MG", "palpite": "Mais de 4.5 cartões", "confianca": 57},
        ],
        "Libertadores": [
            {"mandante": "Flamengo", "visitante": "River Plate", "palpite": "Mais de 8.5 escanteios", "confianca": 64},
            {"mandante": "Palmeiras", "visitante": "Boca Juniors", "palpite": "Mais de 4.5 cartões", "confianca": 63},
        ],
    }
    return exemplos.get(campeonato, [])


# ---------------- HISTÓRICO ----------------
def salvar_resultado(usuario, campeonato, jogo, resultado):
    historico = read_json(HISTORICO_FILE, [])
    historico.append({
        "usuario": usuario,
        "campeonato": campeonato,
        "jogo": f"{jogo['mandante']} x {jogo['visitante']}",
        "palpite": jogo["palpite"],
        "confianca": jogo["confianca"],
        "resultado": resultado,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })
    write_json(HISTORICO_FILE, historico)


def calcular_acerto():
    historico = read_json(HISTORICO_FILE, [])
    if not historico:
        return 0, 0, 0

    total = len(historico)
    acertos = sum(1 for item in historico if item.get("resultado") == "acerto")
    taxa = round((acertos / total) * 100, 2)
    return taxa, acertos, total


# ---------------- FEEDBACK ----------------
def salvar_feedback(usuario, texto):
    feedbacks = read_json(FEEDBACK_FILE, [])
    feedbacks.append({
        "usuario": usuario,
        "feedback": texto.strip(),
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })
    write_json(FEEDBACK_FILE, feedbacks)


# ---------------- INTERFACE ----------------
st.set_page_config(
    page_title="Analisador Futebol V73 Web",
    page_icon="⚽",
    layout="centered",
)

# Estilos base + responsivo para celular
st.markdown("""
<style>
    .main-title {font-size: 34px; font-weight: 800; margin-bottom: 0;}
    .sub-title {font-size: 16px; color: #666; margin-top: 0;}
    .card {
        border: 1px solid #ddd;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        background: #fafafa;
    }
    .small-muted {color: #666; font-size: 14px;}

    /* ===== RESPONSIVO: ajustes para celular ===== */
    @media (max-width: 640px) {
        /* Empilha colunas (campeonato e botão sair) */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        /* Métricas mais compactas */
        div[data-testid="stMetric"] {
            font-size: 14px;
        }
        /* Cartões mais enxutos */
        .card {
            padding: 10px !important;
        }
        .card h3 {
            font-size: 16px !important;
        }
        /* Botões ocupam largura total */
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
            width: 100% !important;
        }
        /* Reduz título principal */
        .main-title {
            font-size: 24px !important;
        }
        .sub-title {
            font-size: 14px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""


if not st.session_state.logado:
    st.markdown('<p class="main-title">⚽ Analisador Futebol V73 Web</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Primeira parte: login, testes de palpites, acerto e feedback.</p>', unsafe_allow_html=True)

    with st.form("login_form"):
        user = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if check_login(user, password):
            st.session_state.logado = True
            st.session_state.usuario = user.strip().lower()
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.info("Login inicial: magdiel / 1234 ou amigo / 1234")

else:
    st.markdown('<p class="main-title">⚽ Analisador Futebol V73 Web</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">Usuário conectado: <b>{st.session_state.usuario}</b></p>', unsafe_allow_html=True)

    col_top1, col_top2 = st.columns([2, 1])
    with col_top1:
        campeonato = st.selectbox("Escolha o campeonato", [
            "Brasileirão Série A",
            "Brasileirão Série B",
            "Copa do Brasil",
            "Libertadores",
        ])
    with col_top2:
        if st.button("Sair"):
            st.session_state.logado = False
            st.session_state.usuario = ""
            st.rerun()

    taxa, acertos, total = calcular_acerto()
    c1, c2, c3 = st.columns(3)
    c1.metric("Acertabilidade", f"{taxa}%")
    c2.metric("Acertos", acertos)
    c3.metric("Total", total)

    st.divider()
    st.subheader("Jogos e palpites de teste")
    st.caption("Nesta primeira parte os jogos ainda são exemplos. A próxima etapa conecta isso aos dados reais.")

    jogos = get_jogos(campeonato)
    for idx, jogo in enumerate(jogos):
        with st.container():
            st.markdown(f"""
            <div class="card">
                <h3>{jogo['mandante']} x {jogo['visitante']}</h3>
                <p><b>Palpite:</b> {jogo['palpite']}</p>
                <p class="small-muted">Confiança inicial: {jogo['confianca']}%</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Marcar acerto", key=f"acerto_{campeonato}_{idx}"):
                    salvar_resultado(st.session_state.usuario, campeonato, jogo, "acerto")
                    st.success("Registrado como acerto.")
                    st.rerun()
            with col2:
                if st.button("❌ Marcar erro", key=f"erro_{campeonato}_{idx}"):
                    salvar_resultado(st.session_state.usuario, campeonato, jogo, "erro")
                    st.error("Registrado como erro.")
                    st.rerun()

    st.divider()
    st.subheader("💬 Feedback do testador")
    with st.form("feedback_form"):
        feedback = st.text_area("Escreva uma sugestão, erro encontrado ou melhoria desejada")
        enviar_feedback = st.form_submit_button("Enviar feedback")

    if enviar_feedback:
        if feedback.strip():
            salvar_feedback(st.session_state.usuario, feedback)
            st.success("Feedback salvo.")
        else:
            st.warning("Digite alguma coisa antes de enviar.")

    with st.expander("Ver últimos registros"):
        historico = read_json(HISTORICO_FILE, [])
        if not historico:
            st.write("Nenhum resultado registrado ainda.")
        else:
            for item in reversed(historico[-10:]):
                st.write(f"{item['data']} — {item['usuario']} — {item['jogo']} — {item['palpite']} — {item['resultado']}")

    with st.expander("Ver feedbacks"):
        feedbacks = read_json(FEEDBACK_FILE, [])
        if not feedbacks:
            st.write("Nenhum feedback ainda.")
        else:
            for item in reversed(feedbacks[-10:]):
                st.write(f"{item['data']} — {item['usuario']}: {item['feedback']}")