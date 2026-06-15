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

st.markdown("<div class='main-title'>🛡️ KI Office Boost – HyperScalelow_html=Tru