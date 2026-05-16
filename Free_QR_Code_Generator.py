import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer,
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    VerticalGradiantColorMask,
)
from PIL import Image, ImageDraw
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QR Studio",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0a0a; color: #f0f0f0; }

.qr-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem; font-weight: 800; letter-spacing: -0.04em;
    background: linear-gradient(135deg, #ffffff 0%, #666 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1;
}
.qr-sub {
    font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #444;
    letter-spacing: 0.18em; text-transform: uppercase;
    margin-top: 0.3rem; margin-bottom: 1.8rem;
}
.sec {
    font-family: 'Space Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.22em; text-transform: uppercase; color: #444;
    margin-bottom: 0.3rem; margin-top: 1rem;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0f2010; border: 1px solid #1a4020; border-radius: 20px;
    padding: 3px 10px; font-family: 'Space Mono', monospace;
    font-size: 0.6rem; color: #4caf50; letter-spacing: 0.1em;
}
.live-dot {
    width: 6px; height: 6px; background: #4caf50; border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.badge {
    display: inline-block; background: #141414; border: 1px solid #222;
    border-radius: 20px; padding: 0.15rem 0.65rem;
    font-family: 'Space Mono', monospace; font-size: 0.62rem; color: #666;
    margin-right: 0.4rem; margin-top: 0.3rem;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #141414 !important; border: 1px solid #222 !important;
    color: #f0f0f0 !important; border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #444 !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.04) !important;
}
.stSlider > div > div > div > div { background: #fff !important; }

.stButton > button {
    background: #fff !important; color: #000 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.85rem !important; letter-spacing: 0.05em !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important; width: 100% !important;
}
.stButton > button:hover { background: #ddd !important; }

.stDownloadButton > button {
    background: #141414 !important; color: #fff !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    border: 1px solid #2a2a2a !important; border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important; width: 100% !important;
}
.stDownloadButton > button:hover { background: #1e1e1e !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #111; border-radius: 10px; padding: 4px; gap: 4px;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #444 !important;
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 0.75rem !important;
    letter-spacing: 0.05em !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: #1e1e1e !important; color: #fff !important; }

hr { border: none; border-top: 1px solid #1a1a1a; margin: 1.2rem 0; }
#MainMenu, footer, header { visibility: hidden; }
.stCheckbox > label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important; color: #888 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def generate_qr(
    data, error_correction, box_size, border,
    style, fill_color, back_color, gradient, gradient_color2,
    logo, logo_size_pct,
) -> Image.Image:

    ec_map = {
        "L — 7%":  qrcode.constants.ERROR_CORRECT_L,
        "M — 15%": qrcode.constants.ERROR_CORRECT_M,
        "Q — 25%": qrcode.constants.ERROR_CORRECT_Q,
        "H — 30%": qrcode.constants.ERROR_CORRECT_H,
    }
    drawer_map = {
        "Carré":               SquareModuleDrawer(),
        "Carré espacé":        GappedSquareModuleDrawer(),
        "Cercle":              CircleModuleDrawer(),
        "Arrondi":             RoundedModuleDrawer(),
        "Barres verticales":   VerticalBarsDrawer(),
        "Barres horizontales": HorizontalBarsDrawer(),
    }
    fill_rgb = hex_to_rgb(fill_color)
    back_rgb = hex_to_rgb(back_color)
    grad_rgb = hex_to_rgb(gradient_color2)

    mask_map = {
        "Uni":                SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb),
        "Dégradé radial":     RadialGradiantColorMask(back_color=back_rgb, center_color=fill_rgb, edge_color=grad_rgb),
        "Dégradé carré":      SquareGradiantColorMask(back_color=back_rgb, center_color=fill_rgb, edge_color=grad_rgb),
        "Dégradé horizontal": HorizontalGradiantColorMask(back_color=back_rgb, left_color=fill_rgb, right_color=grad_rgb),
        "Dégradé vertical":   VerticalGradiantColorMask(back_color=back_rgb, top_color=fill_rgb, bottom_color=grad_rgb),
    }

    qr = qrcode.QRCode(
        error_correction=ec_map.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer_map.get(style, SquareModuleDrawer()),
        color_mask=mask_map.get(gradient, mask_map["Uni"]),
    ).convert("RGBA")

    if logo:
        img_w, img_h = img.size
        max_logo = int(min(img_w, img_h) * logo_size_pct)
        logo_r = logo.convert("RGBA").copy()
        logo_r.thumbnail((max_logo, max_logo), Image.LANCZOS)
        lw, lh = logo_r.size
        pad = 10
        bg  = Image.new("RGBA", (lw + pad*2, lh + pad*2), (255,255,255,255))
        msk = Image.new("L", bg.size, 0)
        ImageDraw.Draw(msk).rounded_rectangle([0, 0, *bg.size], radius=12, fill=255)
        bg.putalpha(msk)
        img.paste(bg,     ((img_w - bg.size[0])//2, (img_h - bg.size[1])//2), bg)
        img.paste(logo_r, ((img_w - lw)//2,          (img_h - lh)//2),         logo_r)

    return img


def img_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.convert("RGB" if fmt == "JPEG" else "RGBA").save(buf, format=fmt)
    return buf.getvalue()


# ── Session state init ────────────────────────────────────────────────────────
for key, default in [("logo_img", None), ("last_params", None), ("cached_qr", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
col_ctrl, col_prev = st.columns([1, 1], gap="large")


# ═══════════════════════ LEFT — Controls ══════════════════════════════════════
with col_ctrl:
    st.markdown('<p class="qr-title">QR Studio</p>', unsafe_allow_html=True)
    st.markdown('<p class="qr-sub">Générateur de QR codes personnalisés</p>', unsafe_allow_html=True)

    tab_content, tab_style, tab_logo = st.tabs(["◼  Contenu", "◈  Style", "⊕  Logo"])

    # ── Tab Contenu ───────────────────────────────────────────────────────────
    with tab_content:
        st.markdown('<p class="sec">Type de contenu</p>', unsafe_allow_html=True)
        content_type = st.selectbox(
            "Type", ["URL","Texte libre","Email","Téléphone","SMS","Wi-Fi","vCard"],
            label_visibility="collapsed",
        )

        st.markdown('<p class="sec">Données</p>', unsafe_allow_html=True)

        if content_type == "URL":
            url     = st.text_input("URL", value="https://www.oca.eu/fr/accueil", placeholder="https://…", label_visibility="collapsed")
            qr_data = url or "https://www.oca.eu/fr/accueil"
            
        elif content_type == "Texte libre":
            txt     = st.text_area("Texte", placeholder="Votre texte…", height=90, label_visibility="collapsed")
            qr_data = txt or "Texte vide"

        elif content_type == "Email":
            email   = st.text_input("Email", placeholder="exemple@domaine.com", label_visibility="collapsed")
            subject = st.text_input("Sujet")
            body    = st.text_area("Corps", height=70)
            qr_data = f"mailto:{email or 'exemple@domaine.com'}?subject={subject}&body={body}"

        elif content_type == "Téléphone":
            phone   = st.text_input("Numéro", placeholder="+33 6 00 00 00 00", label_visibility="collapsed")
            qr_data = f"tel:{phone or '+330000000000'}"

        elif content_type == "SMS":
            phone_s = st.text_input("Numéro", placeholder="+33 6 00 00 00 00", label_visibility="collapsed")
            sms_msg = st.text_area("Message", height=70, label_visibility="collapsed")
            qr_data = f"sms:{phone_s or '+330000000000'}?body={sms_msg}"

        elif content_type == "Wi-Fi":
            ssid  = st.text_input("SSID", placeholder="Nom du réseau")
            wpass = st.text_input("Mot de passe", type="password")
            enc   = st.selectbox("Sécurité", ["WPA","WEP","Aucune"])
            qr_data = f"WIFI:T:{'  ' if enc=='Aucune' else enc};S:{ssid or 'MonReseau'};P:{wpass};;"

        elif content_type == "vCard":
            c1, c2 = st.columns(2)
            with c1: first = st.text_input("Prénom")
            with c2: last  = st.text_input("Nom")
            v_ph = st.text_input("Téléphone")
            v_em = st.text_input("Email")
            v_or = st.text_input("Organisation")
            qr_data = (
                f"BEGIN:VCARD\nVERSION:3.0\n"
                f"N:{last};{first}\nFN:{first} {last}\n"
                f"TEL:{v_ph}\nEMAIL:{v_em}\nORG:{v_or}\nEND:VCARD"
            )

        st.markdown('<p class="sec">Correction d\'erreur</p>', unsafe_allow_html=True)
        error_corr = st.selectbox(
            "EC", ["L — 7%","M — 15%","Q — 25%","H — 30%"],
            index=3, label_visibility="collapsed",
            help="H recommandé avec un logo",
        )

    # ── Tab Style ─────────────────────────────────────────────────────────────
    with tab_style:
        st.markdown('<p class="sec">Forme des modules</p>', unsafe_allow_html=True)
        module_style = st.selectbox(
            "Forme",
            ["Carré","Carré espacé","Cercle","Arrondi","Barres verticales","Barres horizontales"],
            label_visibility="collapsed",
        )

        c_fc, c_bc = st.columns(2)
        with c_fc:
            st.markdown('<p class="sec">Couleur QR</p>', unsafe_allow_html=True)
            fill_color = st.color_picker("QR", value="#000000", label_visibility="collapsed")
        with c_bc:
            st.markdown('<p class="sec">Fond</p>', unsafe_allow_html=True)
            back_color = st.color_picker("Fond", value="#ffffff", label_visibility="collapsed")

        st.markdown('<p class="sec">Dégradé</p>', unsafe_allow_html=True)
        gradient_type = st.selectbox(
            "Dégradé",
            ["Uni","Dégradé radial","Dégradé carré","Dégradé horizontal","Dégradé vertical"],
            label_visibility="collapsed",
        )
        if gradient_type != "Uni":
            st.markdown('<p class="sec">Couleur secondaire</p>', unsafe_allow_html=True)
            grad_color2 = st.color_picker("Couleur 2", value="#6c63ff", label_visibility="collapsed")
        else:
            grad_color2 = fill_color

        st.markdown('<p class="sec">Taille & marge</p>', unsafe_allow_html=True)
        c_sz, c_br = st.columns(2)
        with c_sz: box_size = st.slider("Taille (px/module)", 5, 20, 10)
        with c_br: border   = st.slider("Marge (modules)",    1,  8,  4)

    # ── Tab Logo ──────────────────────────────────────────────────────────────
    with tab_logo:
        st.markdown('<p class="sec">Fichier logo (PNG, JPG, WEBP)</p>', unsafe_allow_html=True)
        logo_file = st.file_uploader("Logo", type=["png","jpg","jpeg","webp"], label_visibility="collapsed")
        if logo_file:
            st.session_state.logo_img = Image.open(logo_file)
        if st.session_state.logo_img:
            st.image(st.session_state.logo_img, width=90, caption="Logo chargé")
            if st.button("✕  Supprimer le logo"):
                st.session_state.logo_img = None
                st.rerun()

        st.markdown('<p class="sec">Taille du logo (% du QR)</p>', unsafe_allow_html=True)
        logo_pct = st.slider("Taille logo", 0.10, 0.35, 0.25, 0.01, label_visibility="collapsed")
        st.caption("💡 Utilisez la correction H pour garantir la lisibilité avec un logo.")

    logo_img = st.session_state.logo_img


# ═══════════════════════ RIGHT — Live Preview ══════════════════════════════════
with col_prev:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
                margin-bottom:0.8rem;margin-top:0.2rem;">
        <span style="font-family:'Space Mono',monospace;font-size:0.6rem;
                     letter-spacing:0.22em;text-transform:uppercase;color:#333;">Aperçu</span>
        <span class="live-badge"><span class="live-dot"></span> LIVE</span>
    </div>
    """, unsafe_allow_html=True)

    # Fingerprint all parameters
    current_params = (
        qr_data, error_corr, box_size, border,
        module_style, fill_color, back_color,
        gradient_type, grad_color2,
        id(logo_img), logo_pct,
    )

    preview_slot = st.empty()
    badges_slot  = st.empty()
    dl_slot      = st.empty()

    # Always regenerate if params changed (Streamlit re-runs on every widget change)
    if current_params != st.session_state.last_params:
        with preview_slot.container():
            with st.spinner("Génération…"):
                qr_img = generate_qr(
                    data=qr_data,
                    error_correction=error_corr,
                    box_size=box_size,
                    border=border,
                    style=module_style,
                    fill_color=fill_color,
                    back_color=back_color,
                    gradient=gradient_type,
                    gradient_color2=grad_color2,
                    logo=logo_img,
                    logo_size_pct=logo_pct,
                )
        st.session_state.cached_qr   = qr_img
        st.session_state.last_params = current_params
    else:
        qr_img = st.session_state.cached_qr

    if qr_img:
        preview_slot.image(qr_img, use_container_width=True)

        w, h = qr_img.size
        badges_slot.markdown(
            f'<span class="badge">◼ {w}×{h} px</span>'
            f'<span class="badge">◈ {module_style}</span>'
            f'<span class="badge">⊕ {gradient_type}</span>'
            + (f'<span class="badge">⊙ logo</span>' if logo_img else ""),
            unsafe_allow_html=True,
        )

        with dl_slot.container():
            st.markdown('<p class="sec" style="margin-top:1rem;">Télécharger</p>', unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "↓  PNG",
                    data=img_to_bytes(qr_img, "PNG"),
                    file_name="qrcode.png",
                    mime="image/png",
                )
            with d2:
                st.download_button(
                    "↓  JPEG",
                    data=img_to_bytes(qr_img, "JPEG"),
                    file_name="qrcode.jpg",
                    mime="image/jpeg",
                )
    else:
        preview_slot.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:420px;background:#0e0e0e;border:1px dashed #1e1e1e;border-radius:16px;
                    color:#2a2a2a;font-family:'Space Mono',monospace;font-size:0.7rem;
                    letter-spacing:0.1em;text-align:center;gap:1rem;">
            <div style="font-size:2.5rem;line-height:1.3;opacity:0.4;">◼◻◼<br>◻◼◻<br>◼◻◼</div>
            <p style="margin:0;">Saisissez du contenu<br>pour voir l'aperçu</p>
        </div>
        """, unsafe_allow_html=True)
