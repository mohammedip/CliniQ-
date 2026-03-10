import streamlit as st
import requests

API_URL = "http://backend:8000"

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CliniQ",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

* { font-family: 'DM Sans', sans-serif; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117;
    color: #e6edf3;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #1a2744 0%, #0d1117 60%);
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
    color: #e6edf3;
}

.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #58a6ff;
    letter-spacing: -1px;
    text-align: center;
    margin-bottom: 0.2rem;
}

.logo-sub {
    text-align: center;
    color: #8b949e;
    font-size: 0.9rem;
    margin-bottom: 2rem;
    font-weight: 300;
}

[data-testid="stTabs"] button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500;
    color: #8b949e !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom-color: #58a6ff !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextInput"] input:focus {
    background: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
    color: #000000 !important;
}

[data-testid="stButton"] button {
    background: #1f6feb !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    width: 100%;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease;
}
[data-testid="stButton"] button:hover {
    background: #388bfd !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(31, 111, 235, 0.4) !important;
}

.msg-user {
    background: rgba(31, 111, 235, 0.15);
    border: 1px solid rgba(31, 111, 235, 0.3);
    border-radius: 12px 12px 4px 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    margin-left: 20%;
    color: #cae8ff;
    font-size: 0.95rem;
}

.msg-bot {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px 12px 12px 4px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    margin-right: 20%;
    color: #e6edf3;
    font-size: 0.95rem;
    line-height: 1.6;
}

.msg-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.5;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.5rem;
}

.topbar-name {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #58a6ff;
}

.topbar-user {
    font-size: 0.85rem;
    color: #8b949e;
}

.badge {
    display: inline-block;
    background: rgba(31,111,235,0.2);
    color: #58a6ff;
    border: 1px solid rgba(31,111,235,0.3);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.alert-error {
    background: rgba(248, 81, 73, 0.1);
    border: 1px solid rgba(248, 81, 73, 0.3);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #ff7b72;
    font-size: 0.9rem;
    margin: 0.5rem 0;
}

.alert-success {
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid rgba(63, 185, 80, 0.3);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #3fb950;
    font-size: 0.9rem;
    margin: 0.5rem 0;
}

.history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.history-question {
    color: #58a6ff;
    font-weight: 500;
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
}

.history-answer {
    color: #8b949e;
    font-size: 0.85rem;
    line-height: 1.5;
}

.history-date {
    color: #484f58;
    font-size: 0.75rem;
    margin-top: 0.4rem;
}

[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
}
[data-testid="stBottom"] {
    background-color: #0d1117 !important;
}
[data-testid="stBottom"] > div {
    background-color: #0d1117 !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Session state ─────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting" not in st.session_state:
    st.session_state.waiting = False
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "page" not in st.session_state:
    st.session_state.page = "chat"


# ─── API helpers ───────────────────────────────────────────────────────────────
def api_post(endpoint, payload, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        res = requests.post(f"{API_URL}{endpoint}", json=payload, headers=headers, timeout=120)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "Cannot connect to backend."}, 503
    except Exception as e:
        return {"detail": str(e)}, 500


def api_get(endpoint, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        res = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=30)
        return res.json(), res.status_code
    except requests.exceptions.ConnectionError:
        return {"detail": "Cannot connect to backend."}, 503
    except Exception as e:
        return {"detail": str(e)}, 500


# ─── Auth page ─────────────────────────────────────────────────────────────────
def show_auth_page():
    st.markdown('<div class="logo">CliniQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">Medical Knowledge Assistant</div>', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Sign In", key="login_btn"):
            if not username or not password:
                st.markdown('<div class="alert-error">Please fill in all fields.</div>', unsafe_allow_html=True)
            else:
                data, status = api_post("/auth/login", {"username": username, "password": password})
                if status == 200:
                    st.session_state.token = data["access_token"]
                    me, _ = api_get("/auth/me", token=data["access_token"])
                    st.session_state.username = me.get("username", username)
                    st.session_state.role = me.get("role", "user")
                    st.rerun()
                else:
                    st.markdown(f'<div class="alert-error">❌ {data.get("detail", "Login failed")}</div>', unsafe_allow_html=True)

    with tab_register:
        st.markdown("<br>", unsafe_allow_html=True)
        reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
        reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
        reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Choose a password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create Account", key="register_btn"):
            if not reg_username or not reg_email or not reg_password:
                st.markdown('<div class="alert-error">Please fill in all fields.</div>', unsafe_allow_html=True)
            else:
                data, status = api_post("/auth/register", {
                    "username": reg_username,
                    "email": reg_email,
                    "password": reg_password
                })
                if status == 201:
                    st.markdown('<div class="alert-success">✅ Account created! You can now sign in.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-error">❌ {data.get("detail", "Registration failed")}</div>', unsafe_allow_html=True)


# ─── Top bar ───────────────────────────────────────────────────────────────────
def show_topbar():
    role_badge = f'<span class="badge">{st.session_state.role}</span>'
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-name">CliniQ</div>
        <div class="topbar-user">👤 {st.session_state.username} {role_badge}</div>
    </div>
    """, unsafe_allow_html=True)

    # layout: leave a blank space in the first column, buttons in the next three
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col2:
        if st.button("💬 Chat", key="nav_chat"):
            st.session_state.page = "chat"
            st.rerun()
    with col3:
        if st.button("📋 History", key="nav_history"):
            st.session_state.page = "history"
            st.rerun()
    with col4:
        if st.button("Sign Out", key="logout"):
            for key in ["token", "username", "role", "messages", "waiting", "pending_question"]:
                st.session_state[key] = None if key != "messages" else []
            st.session_state.waiting = False
            st.session_state.page = "chat"
            st.rerun()


# ─── Chat page ─────────────────────────────────────────────────────────────────
def show_chat_page():
    show_topbar()

    if not st.session_state.messages:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 2.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🏥</div>
            <div style="font-family: 'DM Serif Display', serif; font-size: 1.4rem; margin-bottom: 0.5rem;">
                How can I help you today?
            </div>
            <div style="color: #8b949e; font-size: 0.9rem;">
                Ask me anything about the medical documentation.
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-user">
                <div class="msg-label">You</div>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-bot">
                <div class="msg-label">CliniQ</div>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)

    is_waiting = st.session_state.get("waiting", False)
    question = st.chat_input("Ask a question about the medical manual...", disabled=is_waiting)

    if question and not is_waiting:
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.waiting = True
        st.session_state.pending_question = question
        st.rerun()

    if st.session_state.get("waiting") and st.session_state.get("pending_question"):
        with st.spinner("CliniQ is thinking..."):
            data, status = api_post(
                "/queries/ask",
                {"question": st.session_state.pending_question},
                token=st.session_state.token
            )

        if status == 200:
            answer = data.get("answer", "No answer returned.")
        elif status == 401:
            answer = "⚠️ Session expired. Please sign in again."
            st.session_state.token = None
        else:
            answer = f"⚠️ Error: {data.get('detail', 'Something went wrong.')}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.waiting = False
        st.session_state.pending_question = None
        st.rerun()


# ─── History page ──────────────────────────────────────────────────────────────
def show_history_page():
    show_topbar()

    st.markdown("### 📋 Query History")
    st.markdown("<br>", unsafe_allow_html=True)

    data, status = api_get("/queries/history", token=st.session_state.token)

    if status != 200:
        st.markdown(f'<div class="alert-error">❌ Failed to load history: {data.get("detail")}</div>', unsafe_allow_html=True)
        return

    if not data:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
            <div style="color: #8b949e;">No queries yet. Start asking questions!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", len(data))
    with col2:
        if data:
            st.metric("Last Query", data[0]["created_at"][:10])

    st.markdown("<br>", unsafe_allow_html=True)

    # History list
    for item in data:
        date = item["created_at"][:16].replace("T", " ")
        answer_preview = item["response"][:150] + "..." if len(item["response"]) > 150 else item["response"]
        st.markdown(f"""
        <div class="history-item">
            <div class="history-question">❓ {item["query"]}</div>
            <div class="history-answer">{answer_preview}</div>
            <div class="history-date">🕐 {date}</div>
        </div>
        """, unsafe_allow_html=True)


# ─── Main router ───────────────────────────────────────────────────────────────
if st.session_state.token:
    if st.session_state.page == "history":
        show_history_page()
    else:
        show_chat_page()
else:
    show_auth_page()