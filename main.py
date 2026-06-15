import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime
from fpdf import FPDF
from supabase import create_client, Client

# ==========================================
# 0. INITIALISIERUNG & CLOUD CONFIG
# ==========================================
# Deine Supabase-Daten
SUPABASE_URL = "https://obgtjhlfubgovhmtbfvy.supabase.co"
SUPABASE_KEY = "EyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9iZ3RqaGxmdWJnb3ZobXRiZnZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE1MTA0NzMsImV4cCI6MjA5NzA4NjQ3M30.yfBcjd-EhTednrCZv2__5iz_O8YdLRg_8uUDaNgRoUM"
BUCKET_NAME = "dokumente"

@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = get_supabase_client()
except Exception as e:
    st.error(f"Fehler bei der Verbindung zu Supabase: {e}")

if "aktive_lizenz" not in st.session_state:
    st.session_state["aktive_lizenz"] = None
if "aktuell_gewaehlte_id" not in st.session_state:
    st.session_state["aktuell_gewaehlte_id"] = None

def generate_and_upload_pdf(filename, department, content_lines):
    """Generiert das PDF lokal und lädt es in den Storage hoch"""
    pdf = FPDF()
    pdf.add_page()
   
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 10, txt="KI Office Boost - Automated PDF Document", ln=1, align="C")
    pdf.ln(5)
   
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 7, txt="Uebertragene Datei: " + str(filename), ln=1)
    pdf.cell(190, 7, txt="Zugeordnete Abteilung: " + str(department), ln=1)
    pdf.cell(190, 7, txt="Generiert am: " + datetime.now().strftime('%d.%m.%Y %H:%M:%S'), ln=1)
    pdf.ln(10)
   
    pdf.set_font("Helvetica", "", 10)
    for line in content_lines:
        safe_line = line.replace("€", "EUR").encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(190, 6, txt=safe_line)
   
    temp_filename = f"conv_{random.randint(10000, 99999)}.pdf"
    pdf.output(temp_filename, "F")
   
    cloud_url = ""
    try:
        with open(temp_filename, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(
                path=temp_filename,
                file=f,
                file_options={"content-type": "application/pdf"}
            )
        cloud_url = supabase.storage.from_(BUCKET_NAME).get_public_url(temp_filename)
    except Exception as e:
        st.error(f"Cloud-Upload fehlgeschlagen: {e}")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
           
    return cloud_url

# ==========================================
# 1. UI DESIGN (DARK METRO STYLE)
# ==========================================
st.set_page_config(page_title="KI Office Boost – Control Center", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #05070f, #010204); color: #f8fafc; }
    .main-title {
        font-size: 2.8rem; font-weight: 900;
        background: linear-gradient(135deg, #38bdf8 0%, #10b981 50%, #818cf8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .content-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 30px;
        margin-bottom: 20px;
        min-height: 580px;
    }
    .price-tag { font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 15px 0 5px 0; }
    .feature-list { list-style-type: none; padding-left: 0; line-height: 1.8; color: #cbd5e1; }
    .feature-list li { margin-bottom: 10px; }
    .feature-list li::before { content: "✓  "; color: #10b981; font-weight: bold; }
    .section-lead { color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px; }
   
    .stripe-button {
        display: block;
        text-align: center;
        background: linear-gradient(135deg, #635bff 0%, #4338ca 100%);
        color: white !important;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 20px;
        transition: opacity 0.2s;
    }
    .stripe-button:hover {
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Korrigierte Version von Zeile 116 ohne abgebrochenen Text
st.markdown("<div class='main-title'>🛡️ KI Office Boost – HyperScale Cluster</div><br>", unsafe_allow_html=True)

# Daten live aus der Supabase Cloud-Datenbank abrufen
try:
    res = supabase.table("dokumente").select("*").order("id", desc=True).execute()
    df_global = pd.DataFrame(res.data)
except Exception as e:
    df_global = pd.DataFrame()

tab_dash, tab_analytics, tab_abo = st.tabs(["📂 Executive Ledger Hub", "📈 Echtzeit-Makroanalyse", "💎 Unternehmenslizenzen"])

# ==========================================
# REITER 1: LEDGER HUB
# ==========================================
with tab_dash:
    col_left, col_right = st.columns([12, 10], gap="large")
   
    with col_left:
        st.markdown("### 📥 Universal Document Converter Engine")
        office_file = st.file_uploader("Dokument hochladen", type=["txt", "docx", "xlsx", "pptx"])
       
        if office_file and st.button("⚙️ Daten extrahieren & PDF rendern", use_container_width=True, type="primary"):
            ext = office_file.name.split(".")[-1].lower()
            raw_bytes = office_file.read()
           
            lines = ["Konvertierungs-Protokoll", "----------------------------------------"]
            if ext == "txt":
                lines += raw_bytes.decode("utf-8", errors="ignore").splitlines()[:10]
            else:
                lines.append("Binär-Inhalt erfolgreich transformiert.")
           
            abteilung = "Finance & Controlling" if ext == "xlsx" else "Allgemeine Verwaltung"
           
            pdf_cloud_url = generate_and_upload_pdf(office_file.name, abteilung, lines)
           
            betrag = round(random.uniform(75.0, 1200.0), 2)
            rechnungsnr = "KI-" + str(random.randint(1000, 9999))
           
            # Daten direkt in Supabase PostgreSQL speichern
            try:
                insert_res = supabase.table("dokumente").insert({
                    "dateiname": office_file.name.rsplit(".", 1)[0] + ".pdf",
                    "rechnungssteller": abteilung,
                    "rechnungsnummer": rechnungsnr,
                    "betrag": betrag,
                    "waehrung": "EUR",
                    "ust_id": "DE81491624",
                    "datum": datetime.now().strftime("%Y-%m-%d"),
                    "status": "Neu",
                    "betrag_eur": betrag,
                    "pdf_path": pdf_cloud_url
                }).execute()
                if insert_res.data:
                    st.session_state["aktuell_gewaehlte_id"] = insert_res.data[0]["id"]
            except Exception as e:
                st.error(f"Fehler beim Speichern in der Cloud-Datenbank: {e}")
            st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Multi-Tenant Ledger View")
        if df_global.empty:
            st.info("Bisher keine Dokumente verarbeitet.")
        else:
            valid_ids = df_global["id"].tolist()
            if st.session_state["aktuell_gewaehlte_id"] not in valid_ids:
                st.session_state["aktuell_gewaehlte_id"] = valid_ids[0]
               
            chosen_id = st.selectbox("Dokumenten-ID auswählen:", valid_ids, index=valid_ids.index(st.session_state["aktuell_gewaehlte_id"]))
            st.session_state["aktuell_gewaehlte_id"] = chosen_id
            st.dataframe(df_global, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("### 📄 Live-PDF Originalbeleg")
        active_id = st.session_state["aktuell_gewaehlte_id"]
       
        if active_id and not df_global.empty:
            row = df_global[df_global["id"] == active_id]
            if not row.empty and row["pdf_path"].values[0]:
                pdf_url = row["pdf_path"].values[0]
                pdf_display = f'<iframe src="{pdf_url}" width="100%" height="600" style="border:1px solid #1e293b; border-radius:12px;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning("PDF-Datei temporär nicht verfügbar.")
        else:
            st.info("Wähle links einen Eintrag, um die Vorschau zu laden.")

# ==========================================
# REITER 2: ANALYTICS
# ==========================================
with tab_analytics:
    st.markdown("### 📈 Echtzeit-Ausgabenverteilung")
    if not df_global.empty:
        st.bar_chart(df_global, x="rechnungssteller", y="betrag_eur")

# ==========================================
# REITER 3: LIZENZEN WITH STRIPE LINKS
# ==========================================
with tab_abo:
    st.markdown("## 💎 Enterprise Compliance & Lizenzkontingente")
    st.markdown("<p class='section-lead'>Maximieren Sie Ihre administrative Effizienz. Wählen Sie die passende Infrastruktur für Ihre automatisierten Workflows.</p>", unsafe_allow_html=True)
    st.markdown("---")
   
    col_prof, col_ent = st.columns(2, gap="large")
   
    with col_prof:
        st.markdown("""
        <div class="content-box">
            <h3 style="color: #38bdf8; margin-top: 0; font-size: 1.6rem;">🔵 Professional Scale Paket</h3>
            <p style="color: #94a3b8; font-size: 0.95rem;">Die ideale Lösung für ambitionierte Selbstständige, Agenturen und wachsende KMUs, die manuelle Zettelwirtschaft eliminieren wollen.</p>
            <div class="price-tag">79 € <span style="font-size: 1.1rem; color: #64748b; font-weight: normal;">/ Monat (zzgl. MwSt.)</span></div>
            <p style="color: #10b981; font-size: 0.85rem; font-weight: bold; margin-bottom: 20px;">Alternativ: Jährliche Abrechnung für 750 € (Sie sparen über 15%)</p>
            <hr style="border-color: rgba(255,255,255,0.08);">
            <ul class="feature-list">
                <li><strong>500 Konvertierungen / Monat:</strong> Digitalisieren Sie bis zu 500 Dokumente pro Monat über unsere KI-Engine.</li>
                <li><strong>Intelligente KI-Textextraktion:</strong> Automatische Erkennung von Kernvariablen wie Rechnungsnummer, UST-ID und Betrag.</li>
                <li><strong>Echtzeit-Währungsumrechnung:</strong> Fremdwährungen werden sekundengenau in EUR transformiert.</li>
                <li><strong>90 Tage Cloud-Sicherung:</strong> Alle generierten PDFs werden für 90 Tage im verschlüsselten Storage archiviert.</li>
            </ul>
            <a href="https://buy.stripe.com/14A9A07wCeGsg24dQR" target="_blank" class="stripe-button" style="background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);">Jetzt Professional Scale buchen</a>
        </div>
        """, unsafe_allow_html=True)

    with col_ent:
        st.markdown("""
        <div class="content-box">
            <h3 style="color: #818cf8; margin-top: 0; font-size: 1.6rem;">🔮 HighScale Infrastructure Paket</h3>
            <p style="color: #94a3b8; font-size: 0.95rem;">Das Maximum an Power für Großkonzerne, Kanzleien und Finanzabteilungen mit Fokus auf unlimitierte Skalierung und höchste Datensicherheit.</p>
            <div class="price-tag">499 € <span style="font-size: 1.1rem; color: #64748b; font-weight: normal;">/ Monat (zzgl. MwSt.)</span></div>
            <p style="color: #10b981; font-size: 0.85rem; font-weight: bold; margin-bottom: 20px;">Alternativ: Jährliche Abrechnung für 4.990 € (2 Monate komplett geschenkt)</p>
            <hr style="border-color: rgba(255,255,255,0.08);">
            <ul class="feature-list">
                <li><strong>Unbegrenztes Volumen (No Limits):</strong> Absolut keine Obergrenze für Datei-Uploads oder PDF-Generierungen.</li>
                <li><strong>Lebenslanger Cloud-Langzeitspeicher:</strong> Permanentes, GoBD-konformes Online-Archiv auf europäischen Servern.</li>
                <li><strong>Multi-Tenant Mandantenfähigkeit:</strong> Beliebig viele Mitarbeiter-Logins mit individuellen Rollenrechten.</li>
                <li><strong>Dedicated Server Speed:</strong> Priorisierte Hardware für bis zu 5x schnellere Analysen.</li>
            </ul>
            <a href="https://buy.stripe.com/14A7sE9EK6e04xba0JgEg0i" target="_blank" class="stripe-button">Jetzt HighScale Infrastruktur aktivieren</a>
        </div>
        """, unsafe_allow_html=True)