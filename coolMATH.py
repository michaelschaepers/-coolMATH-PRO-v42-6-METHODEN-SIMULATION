# -*- coding: utf-8 -*-
# ==========================================
# DATEI: coolMATH.py
# VERSION: 42.0 (TOTAL MONSTER - SAMSUNG EDITION)
# ZEITSTEMPEL: 17.02.2026 09:47 Uhr
# AUTOR: Michael Schäpers, °coolsulting
# ==========================================
# ÄNDERUNGEN v41.0:
# - Entfernung des Ballens / weißen Balken-Bug
# - 6 Berechnungsmethoden (Praktiker, VDI alt, VDI neu, Recknagel, Kaltluftsee, KI-Hybrid)
# - Samsung Wind-Free Wandgerät Vorschlag aus Datenbank
# - Übergabebericht (JSON/strukturiert) für nächste App
# - Professioneller Kundenbericht (PDF)
# ==========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
import io
import tempfile
from fpdf import FPDF
from datetime import datetime

# --- BRANDING KONSTANTEN ---
APP_VERSION = "42.0 Samsung Edition"
CI_BLUE = "#36A9E1"
CI_GRAY = "#3C3C3B"
CI_WHITE = "#FFFFFF"

def pdf_safe(text):
    """Sanitize text for FPDF (latin-1 only). Replace common non-latin-1 chars."""
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        '°': 'deg',   # °
        '²': '2',     # ²
        '³': '3',     # ³
        'ä': 'ae',    # ä
        'ö': 'oe',    # ö
        'ü': 'ue',    # ü
        'Ä': 'Ae',    # Ä
        'Ö': 'Oe',    # Ö
        'Ü': 'Ue',    # Ü
        'ß': 'ss',    # ß
        '×': 'x',     # ×
        '→': '->',    # →
        '–': '-',     # –
        '—': '--',    # —
        '≥': '>=',    # ≥
        '≤': '<=',    # ≤
        'τ': 'tau',   # τ
        'φ': 'phi',   # φ
        'ε': 'eps',   # ε
        'Δ': 'D',     # Δ
        '★': '*',     # ★
        'é': 'e',     # é
        '€': 'EUR',   # €
        '‘': "'",     # '
        '’': "'",     # '
        '“': '"',     # "
        '”': '"',     # "
    }
    for uni, asc in replacements.items():
        text = text.replace(uni, asc)
    # Final fallback: encode to latin-1, replace remaining unknowns
    return text.encode('latin-1', errors='replace').decode('latin-1')


def pdf_output_bytes(pdf):
    """Universal pdf.output() → bytes for both fpdf and fpdf2"""
    result = pdf.output()
    if isinstance(result, (bytes, bytearray)):
        return bytes(result)
    # Legacy fpdf returns latin-1 string
    return result.encode('latin-1', errors='replace')

# ==========================================
# 1. SETUP & CSS (Kein weißer Balken Bug)
# ==========================================
try:
    st.set_page_config(page_title="coolMATH Pro Simulation", layout="wide", initial_sidebar_state="collapsed")
except Exception:
    pass

def setup_page():
    st.markdown(f"""
        <style>
        /* Basis Reset */
        .stApp {{
            background-color: {CI_BLUE};
            color: white;
        }}
        /* Entfernung des weißen Balken-Bugs */
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {CI_BLUE};
        }}
        [data-testid="stHeader"] {{
            background-color: transparent !important;
            display: none !important;
        }}
        [data-testid="stToolbar"] {{
            display: none !important;
        }}
        [data-testid="stDecoration"] {{
            display: none !important;
        }}
        /* Sidebar verstecken */
        [data-testid="stSidebar"] {{
            display: none;
        }}
        /* Streiche den Deploy-Button */
        .stDeployButton {{
            display: none !important;
        }}
        /* Main container padding */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        /* Typografie */
        .cool-text {{
            color: {CI_WHITE};
            font-weight: 900;
            font-size: 68px;
            line-height: 1;
            display: inline-block;
            vertical-align: bottom;
            letter-spacing: -1px;
        }}
        .math-text {{
            color: {CI_GRAY};
            font-weight: 900;
            font-size: 68px;
            line-height: 1;
            display: inline-block;
            vertical-align: bottom;
            letter-spacing: -1px;
        }}
        .version-badge {{
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            display: inline-block;
            margin-top: 8px;
        }}
        /* Karten */
        .card {{
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            color: {CI_GRAY};
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .card-blue {{
            background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            color: white;
            backdrop-filter: blur(10px);
        }}
        /* Ergebnis Matrix */
        .matrix-wrapper {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-top: 20px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.15);
        }}
        .matrix-title {{
            color: {CI_GRAY};
            font-size: 24px;
            font-weight: 900;
            text-align: center;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        /* Tabellen */
        .styled-table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
        }}
        .styled-table th {{
            background: {CI_GRAY};
            color: white;
            padding: 12px 15px;
            text-align: center !important;
            font-weight: 900;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1px;
        }}
        .styled-table td {{
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
            text-align: center !important;
            font-weight: 700;
            color: {CI_GRAY};
            font-size: 13px;
        }}
        .total-row td {{
            background-color: #f0f8ff;
            font-size: 14px !important;
            border-top: 3px solid {CI_BLUE} !important;
            color: {CI_BLUE} !important;
            font-weight: 900 !important;
        }}
        .samsung-row td {{
            background-color: #e8f5e9;
            color: #2e7d32 !important;
            font-weight: 700;
        }}
        /* ALL labels: uniform white uppercase style */
        label {{
            color: white !important;
            font-weight: 800 !important;
            font-size: 11px !important;
            letter-spacing: 0.8px !important;
            text-transform: uppercase !important;
        }}
        /* Number inputs: preserve m² superscript — no uppercase transform */
        [data-testid="stNumberInput"] label {{
            text-transform: none !important;
            font-weight: 800 !important;
            color: white !important;
            font-size: 11px !important;
            letter-spacing: 0.8px !important;
        }}
        /* Slider label same style */
        [data-testid="stSlider"] label {{
            text-transform: uppercase !important;
        }}
        /* Divider */
        hr {{
            border-color: rgba(255,255,255,0.3) !important;
            margin: 20px 0;
        }}
        /* Expander */
        [data-testid="stExpander"] {{
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        /* Expander header button - readable text */
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] > div > div > div > button,
        [data-testid="stExpander"] > div > div > div > button p,
        [data-testid="stExpander"] > div > div > div > button span {{
            color: white !important;
            font-weight: 900 !important;
            font-size: 13px !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }}
        /* Expander arrow icon */
        [data-testid="stExpander"] svg {{
            stroke: white !important;
            fill: white !important;
        }}
        /* Inputs inside expander: white bg + dark text for readability */
        [data-testid="stExpander"] .stTextInput > div > div > input {{
            background: rgba(255,255,255,0.92) !important;
            color: {CI_GRAY} !important;
            font-weight: 700 !important;
            border: 1px solid rgba(255,255,255,0.5) !important;
        }}
        /* Labels inside expander */
        [data-testid="stExpander"] label {{
            color: white !important;
            font-weight: 800 !important;
            font-size: 11px !important;
            letter-spacing: 1px !important;
        }}
        /* Buttons */
        .stButton > button {{
            background: {CI_GRAY};
            color: white;
            border: none;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-radius: 8px;
            padding: 12px 24px;
        }}
        .stButton > button:hover {{
            background: {CI_BLUE};
            color: white;
            transform: translateY(-1px);
        }}
        /* Download Button */
        .stDownloadButton > button {{
            background: {CI_BLUE};
            color: white;
            border: none;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-radius: 8px;
        }}
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: rgba(255,255,255,0.7);
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 1px;
        }}
        .stTabs [aria-selected="true"] {{
            background: white !important;
            color: {CI_GRAY} !important;
            border-radius: 8px;
        }}
        /* Selectbox, Input — dark text for readability */
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background: rgba(255,255,255,0.92) !important;
            color: {CI_GRAY} !important;
            font-weight: 700 !important;
            border: 1px solid rgba(255,255,255,0.5) !important;
            border-radius: 8px !important;
        }}
        /* Selectbox dropdown — dark text */
        .stSelectbox > div > div {{
            background: rgba(255,255,255,0.92) !important;
            color: {CI_GRAY} !important;
            font-weight: 700 !important;
            border: 1px solid rgba(255,255,255,0.5) !important;
            border-radius: 8px !important;
        }}
        /* Selectbox selected value text */
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] div {{
            color: {CI_GRAY} !important;
            font-weight: 700 !important;
        }}
        /* Number input +/- buttons */
        .stNumberInput button {{
            color: {CI_GRAY} !important;
            background: rgba(255,255,255,0.7) !important;
        }}
        /* Samsung Gerät Karte */
        .samsung-card {{
            background: linear-gradient(135deg, #1a5276, #2e86ab);
            border-radius: 12px;
            padding: 16px;
            color: white;
            margin: 8px 0;
        }}
        .samsung-card-match {{
            background: linear-gradient(135deg, #1e8449, #27ae60);
            border-radius: 12px;
            padding: 16px;
            color: white;
            margin: 8px 0;
        }}
        /* Method Badge */
        .method-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .badge-vdi-n {{ background: #2ecc71; color: white; }}
        .badge-vdi-a {{ background: #f39c12; color: white; }}
        .badge-reck {{ background: {CI_GRAY}; color: white; }}
        .badge-prak {{ background: #e74c3c; color: white; }}
        .badge-klts {{ background: #9b59b6; color: white; }}
        .badge-ki {{ background: #1abc9c; color: white; }}
        /* Section Header */
        .section-header {{
            color: white;
            font-size: 20px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin: 30px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
        }}
        </style>
    """, unsafe_allow_html=True)


# ==========================================
# 2. PHYSIK ENGINE — 6 METHODEN
# ==========================================
HOURS = np.arange(24)

# Solare Einstrahlungsdaten [W/m²] pro Stunde und Ausrichtung
SOLAR_DB = {
    "NORD":      [20,20,20,20,20,40,60,80,100,110,120,120,120,120,110,100,80,60,40,20,20,20,20,20],
    "OST":       [0,0,0,0,100,350,550,650,680,600,450,250,150,100,80,60,40,20,0,0,0,0,0,0],
    "SUED":       [0,0,0,0,0,50,150,300,450,550,620,650,650,620,550,450,300,150,50,0,0,0,0,0],
    "WEST":      [0,0,0,0,0,0,20,50,70,90,110,150,250,450,600,680,650,550,350,150,0,0,0,0],
    "SUED-OST":   [0,0,0,50,200,450,580,650,620,500,350,200,120,90,70,40,20,0,0,0,0,0,0,0],
    "SUED-WEST":  [0,0,0,0,0,0,20,50,80,120,200,350,500,620,650,580,450,250,80,20,0,0,0,0],
}

def get_phys_constants(standard, glass, shade):
    """Physikalische Konstanten je Gebäudestandard"""
    u_vals  = {"Altbau": 1.7, "Bestand": 0.8, "Neubau (GEG)": 0.28, "Passivhaus": 0.15}
    g_vals  = {"Einfach": 0.85, "Doppel": 0.65, "Dreifach": 0.50, "Sonnenschutz": 0.32}
    fc_vals = {"Keine": 1.0, "Vorhang (Innen)": 0.6, "Raffstore (Aussen)": 0.25, "Rollladen": 0.15}
    return u_vals.get(standard, 0.8), g_vals.get(glass, 0.65), fc_vals.get(shade, 1.0)


def calc_praktiker(area, orient, standard, glass, shade, pers, tech):
    """METHODE 1: Praktiker (Heuristik) — q-Wert je Standard, Orientierung, Sonnenschutz REDUZIERT"""
    _, _, fc = get_phys_constants(standard, glass, shade)
    q_std  = {"Altbau": 90.0, "Bestand": 75.0, "Neubau (GEG)": 55.0, "Passivhaus": 35.0}
    q_ori  = {"SUED": 15, "SUED-OST": 12, "SUED-WEST": 12, "WEST": 8, "OST": 5, "NORD": 0}
    q_base = (q_std.get(standard, 75.0) + q_ori.get(orient, 0)) * fc
    q_int  = (pers * 100 + tech) / max(area, 1)
    return np.full(24, area * (q_base + q_int))

def calc_recknagel(area, orient, standard, glass, shade, pers, tech, win_area):
    """METHODE 4: Recknagel — Q_tr (dT standard-abh.) + Q_solar + Q_int"""
    u, g, fc = get_phys_constants(standard, glass, shade)
    sol_raw  = np.array(SOLAR_DB[orient], dtype=float)
    dT_map   = {"Altbau": 9.0, "Bestand": 7.0, "Neubau (GEG)": 5.0, "Passivhaus": 3.0}
    delta_T  = dT_map.get(standard, 6.0)
    q_tr     = area * u * delta_T
    q_st     = sol_raw * win_area * g * fc
    q_int    = np.array([
        (pers * 100 + tech + area * 8) if 8 <= h <= 18 else (pers * 50 + tech * 0.1)
        for h in HOURS])
    return q_tr + q_st + q_int

def calc_vdi_alt(reck_curve):
    """
    METHODE 2: VDI 2078 Alt (1996)
    Pauschaler Zuschlag +15-25% auf Recknagel-Basis
    """
    return reck_curve * 1.20


def calc_vdi_neu(area, orient, standard, glass, shade, pers, tech, win_area, bau_m):
    """METHODE 3: VDI 6007 — RC-Tiefpass, gleiche Eingangslast wie Recknagel"""
    u, g, fc = get_phys_constants(standard, glass, shade)
    sol_raw  = np.array(SOLAR_DB[orient], dtype=float)
    tau      = {"Schwer (Beton/Stein)": 18.0, "Mittel (Ziegel/Holz-Beton)": 10.0, "Leicht (Holz/Trockenbau)": 4.0}.get(bau_m, 10.0)
    delta_T  = {"Altbau": 9.0, "Bestand": 7.0, "Neubau (GEG)": 5.0, "Passivhaus": 3.0}.get(standard, 6.0)
    q_ext    = (area * u * delta_T + sol_raw * win_area * g * fc
                + np.array([(pers*100+tech+area*8) if 8<=h<=18 else (pers*50+tech*0.1) for h in HOURS]))
    q_vdi    = np.zeros(24)
    for _ in range(4):  # 96h Einschwingen
        for h in range(24):
            q_prev   = q_vdi[(h-1)%24]
            q_vdi[h] = q_prev + (q_ext[h] - q_prev) / (tau + 1)
    return q_vdi


def calc_kaltluftsee(area, orient, standard, glass, shade, pers, tech, win_area, bau_m, raumhoehe=2.5):
    """METHODE 5: Kaltluftsee — Recknagel / epsilon (eps=1.3 → 23% Reduktion)"""
    return calc_recknagel(area, orient, standard, glass, shade, pers, tech, win_area) / 1.3


def calc_ki_hybrid(area, orient, standard, glass, shade, pers, tech, win_area, bau_m):
    """METHODE 6: KI-Hybrid — Phasenverschiebung + Daempfung + Pre-Cooling"""
    u, g, fc  = get_phys_constants(standard, glass, shade)
    sol_raw   = np.array(SOLAR_DB[orient], dtype=float)
    delta_T   = {"Altbau": 9.0, "Bestand": 7.0, "Neubau (GEG)": 5.0, "Passivhaus": 3.0}.get(standard, 6.0)
    phi       = {"Schwer (Beton/Stein)": 10, "Mittel (Ziegel/Holz-Beton)": 6, "Leicht (Holz/Trockenbau)": 2}.get(bau_m, 6)
    f         = {"Schwer (Beton/Stein)": 0.55, "Mittel (Ziegel/Holz-Beton)": 0.70, "Leicht (Holz/Trockenbau)": 0.88}.get(bau_m, 0.70)
    q_sol     = np.roll(sol_raw, phi) * f * win_area * g * fc
    q_tr      = area * u * delta_T
    q_int     = np.array([(pers*100+tech+area*6) if 8<=h<=18 else (pers*50+tech*0.05) for h in HOURS])
    pre_cool  = np.array([0.75 if 0<=h<=6 else 1.0 for h in HOURS])
    return (q_sol + q_tr + q_int) * pre_cool


# ==========================================
# 3. SAMSUNG DATENBANK — Wind-Free Wandgeräte
# ==========================================

# Samsung Wind-Free Standard Wandgeräte (AR-Serie)
SAMSUNG_WINDFREE_WALL = {
    # Leistungsklasse kW: {Model, Art.Nr, Kühlen kW, Heizen kW, SEER, SCOP, EER, Preis_LP}
    2.0:  {"model": "Wind-Free Comfort 07",  "art_nr": "AR07TXFCAWKNEU", "cool_kw": 2.0,  "heat_kw": 2.5,  "seer": 6.2, "scop": 4.6, "eer": 3.56, "preis": 749.0,  "btus": "7.000"},
    2.5:  {"model": "Wind-Free Comfort 09",  "art_nr": "AR09TXFCAWKNEU", "cool_kw": 2.5,  "heat_kw": 3.2,  "seer": 6.2, "scop": 4.6, "eer": 3.56, "preis": 849.0,  "btus": "9.000"},
    3.5:  {"model": "Wind-Free Comfort 12",  "art_nr": "AR12TXFCAWKNEU", "cool_kw": 3.5,  "heat_kw": 4.0,  "seer": 6.2, "scop": 4.6, "eer": 3.56, "preis": 999.0,  "btus": "12.000"},
    5.0:  {"model": "Wind-Free Comfort 18",  "art_nr": "AR18TXFCAWKNEU", "cool_kw": 5.0,  "heat_kw": 6.0,  "seer": 6.1, "scop": 4.0, "eer": 3.40, "preis": 1299.0, "btus": "18.000"},
}

SAMSUNG_SIZES_KW = sorted(SAMSUNG_WINDFREE_WALL.keys())

def find_samsung_device(peak_watt, safety_factor=1.10):
    """
    Findet passendes Samsung Wind-Free Wandgerät
    safety_factor: 15% Überdimensionierung (Norm-Empfehlung)
    Gibt primäres und alternatives Gerät zurück
    """
    required_kw = (peak_watt * safety_factor) / 1000.0
    
    # Primär: kleinstes Gerät >= required_kw
    primary = None
    for kw in SAMSUNG_SIZES_KW:
        if kw >= required_kw:
            primary = SAMSUNG_WINDFREE_WALL[kw].copy()
            primary["kw_class"] = kw
            primary["required_kw"] = required_kw
            primary["peak_w"] = peak_watt
            break
    
    # Fallback: größtes verfügbares
    if primary is None:
        kw = SAMSUNG_SIZES_KW[-1]
        primary = SAMSUNG_WINDFREE_WALL[kw].copy()
        primary["kw_class"] = kw
        primary["required_kw"] = required_kw
        primary["peak_w"] = peak_watt
        primary["oversized"] = True
    
    # Alternativ: nächstkleineres (wenn Auslegung knapp)
    alt = None
    idx = SAMSUNG_SIZES_KW.index(primary["kw_class"])
    if idx > 0:
        alt_kw = SAMSUNG_SIZES_KW[idx - 1]
        alt = SAMSUNG_WINDFREE_WALL[alt_kw].copy()
        alt["kw_class"] = alt_kw
    
    return primary, alt


def load_samsung_from_file():
    """Versucht Samsung-Daten aus Excel-Datei zu laden (falls vorhanden)"""
    try:
        samsung_files = [f for f in os.listdir('.') 
                        if any(kw in f.lower() for kw in ['samsung', 'mtf', 'klima', 'artikel']) 
                        and f.endswith('.xlsx')]
        if samsung_files:
            df = pd.read_excel(samsung_files[0], engine='openpyxl')
            # Nur Wandgeräte / Wind-Free filtern
            if 'Bezeichnung' in df.columns:
                mask = df['Bezeichnung'].astype(str).str.contains('Wind.?Free|Wandgerät|AR[0-9]', 
                                                                    case=False, regex=True)
                df_wf = df[mask].copy()
                if len(df_wf) > 0:
                    return df_wf
    except Exception:
        pass
    return None


# ==========================================
# 4. PDF ENGINE — CORPORATE DESIGN
# ==========================================
class CoolMATHReport(FPDF):
    def __init__(self, proj, kunde, bearbeiter, firma, report_type="simulation"):
        super().__init__()
        self.proj = proj
        self.kunde = kunde
        self.bearbeiter = bearbeiter
        self.firma = firma
        self.datum = datetime.now().strftime("%d.%m.%Y")
        self.report_type = report_type  # "simulation" oder "kunde"

    def header(self):
        # Blauer Header-Balken
        self.set_fill_color(54, 169, 225)
        self.rect(0, 0, 210, 48, 'F')
        
        # Logo
        logo_opts = [
            "Coolsulting_Logo_ohneHG_outlines_weiss.png",
            "Coolsulting_Logo_ohneHG_weiss.png",
        ]
        for logo in logo_opts:
            if os.path.exists(logo):
                try:
                    self.image(logo, x=125, y=5, w=75)
                except:
                    pass
                break
        
        # Titel
        self.set_text_color(255, 255, 255)
        if self.report_type == "kunde":
            self.set_font('Arial', 'B', 20)
            self.set_xy(10, 10)
            self.cell(0, 10, pdf_safe('KLIMAANLAGEN-ANALYSE & EMPFEHLUNG'), 0, 0, 'L')
        else:
            self.set_font('Arial', 'B', 20)
            self.set_xy(10, 10)
            self.cell(0, 10, pdf_safe('SIMULATIONS-ANALYSE - TECHNIKÜBERGABE'), 0, 0, 'L')
        
        self.set_font('Arial', '', 8)
        self.set_xy(10, 24)
        self.cell(0, 5, pdf_safe(f'PROJEKT: {self.proj.upper()} | KUNDE: {self.kunde.upper()}'), 0, 1)
        self.set_xy(10, 29)
        self.cell(0, 5, pdf_safe(f'BEARBEITER: {self.bearbeiter.upper()} | FIRMA: {self.firma.upper()}'), 0, 1)
        self.set_xy(10, 34)
        self.cell(0, 5, pdf_safe(f'DATUM: {self.datum} | VERSION: {APP_VERSION}'), 0, 1)
        
        # Unterlinie
        self.set_draw_color(255, 255, 255)
        self.set_line_width(0.3)
        self.line(10, 45, 200, 45)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, pdf_safe(f'coolMATH Pro {APP_VERSION} | {self.datum} | Seite {self.page_no()}'), 0, 0, 'C')

    def add_section_title(self, title, subtitle=""):
        self.ln(8)
        self.set_font('Arial', 'B', 13)
        self.set_text_color(54, 169, 225)
        self.cell(0, 8, pdf_safe(title).upper(), 0, 1, 'L')
        if subtitle:
            self.set_font('Arial', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, pdf_safe(subtitle), 0, 1, 'L')
        self.set_draw_color(54, 169, 225)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def add_info_box(self, text, bg_rgb=(240, 248, 255)):
        self.set_fill_color(*bg_rgb)
        self.set_text_color(60, 60, 59)
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 6, pdf_safe(text), 1, 'L', True)
        self.ln(4)

    def add_table_row(self, cells, widths, is_header=False, is_total=False):
        if is_header:
            self.set_fill_color(60, 60, 59)
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 9)
        elif is_total:
            self.set_fill_color(54, 169, 225)
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 10)
        else:
            self.set_fill_color(248, 248, 248)
            self.set_text_color(60, 60, 59)
            self.set_font('Arial', '', 9)
        
        for cell, w in zip(cells, widths):
            self.cell(w, 8, pdf_safe(str(cell)), 1, 0, 'C', is_header or is_total)
        self.ln()

    def add_plot(self, img_bytes, title="", w=180):
        if title:
            self.add_section_title(title)
        # Write bytes to named temp file so fpdf can detect PNG format
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name
        try:
            self.image(tmp_path, x=15, y=self.get_y(), w=w)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        self.ln(85)


# ==========================================
# 5. ÜBERGABE-BERICHT JSON
# ==========================================
def build_transfer_report(proj, kunde, bearbeiter, firma, room_results, g_sums,
                           samsung_recommendations, selected_hw, total_installed_kw):
    """Erstellt strukturierten JSON-Übergabebericht für coolMATCH"""
    report = {
        "meta": {
            "app": "coolMATH",
            "version": APP_VERSION,
            "datum": datetime.now().isoformat(),
            "projekt": proj,
            "kunde": kunde,
            "bearbeiter": bearbeiter,
            "firma": firma
        },
        "kuehllasten_gesamt": {
            "vdi_neu_peak_w": int(np.max(g_sums["VDI_N"])),
            "vdi_alt_peak_w": int(np.max(g_sums["VDI_A"])),
            "recknagel_peak_w": int(np.max(g_sums["RECK"])),
            "praktiker_peak_w": int(np.max(g_sums["PRAK"])),
            "kaltluftsee_peak_w": int(np.max(g_sums["KLTS"])),
            "ki_hybrid_peak_w": int(np.max(g_sums["KI"])),
            "installiert_kw": total_installed_kw
        },
        "zonen": [],
        "samsung_empfehlungen": []
    }
    
    for r in room_results:
        report["zonen"].append({
            "zone": r["ZONE"],
            "vdi_neu_w": r["VDI NEU"],
            "vdi_alt_w": r["VDI ALT"],
            "recknagel_w": r["RECKNAGEL"],
            "praktiker_w": r["PRAKTIKER"],
            "kaltluftsee_w": r.get("KALTLUFTSEE", 0),
            "ki_hybrid_w": r.get("KI HYBRID", 0),
        })
    
    for sr in samsung_recommendations:
        if sr:
            report["samsung_empfehlungen"].append({
                "zone": sr.get("zone", ""),
                "model": sr.get("primary", {}).get("model", ""),
                "art_nr": sr.get("primary", {}).get("art_nr", ""),
                "kw_class": sr.get("primary", {}).get("kw_class", 0),
                "preis_lp": sr.get("primary", {}).get("preis", 0),
                "required_kw": round(sr.get("primary", {}).get("required_kw", 0), 2)
            })
    
    return report


# ==========================================
# 6. MATPLOTLIB CHART FÜR PDF
# ==========================================
def make_pdf_chart(profiles, total, title, mode_key, hours=HOURS):
    """Erstellt Matplotlib-Chart für PDF-Export"""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafafa')
    
    colors = ['#36A9E1', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
    for idx, p in enumerate(profiles):
        ax.plot(hours, p[mode_key], alpha=0.6, linewidth=1.5, 
                label=p["name"], color=colors[idx % len(colors)], linestyle='--')
    
    ax.plot(hours, total, color='#3C3C3B', linewidth=3.5, label='GESAMT SIMULTAN', zorder=5)
    
    ax.set_title(title, fontweight='bold', fontsize=12, color='#3C3C3B')
    ax.set_xlabel('Stunde', fontsize=9)
    ax.set_ylabel('Kuhllast [W]', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper left', fontsize=8, ncol=3)
    ax.set_xlim(0, 23)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    return buf.getvalue()


def make_comparison_chart(g_sums, hours=HOURS):
    """Erstellt Vergleichs-Chart aller Methoden für PDF"""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#fafafa')
    
    method_colors = {
        "VDI NEU (VDI 6007)": ('#36A9E1', 3.5, '-'),
        "VDI ALT (2078-1996)": ('#F39C12', 2.0, '--'),
        "Recknagel":           ('#3C3C3B', 2.0, ':'),
        "Praktiker":           ('#E74C3C', 2.5, '-.'),
        "Kaltluftsee":         ('#9B59B6', 2.0, '--'),
        "KI-Hybrid":           ('#1ABC9C', 2.5, '-'),
    }
    key_map = {
        "VDI NEU (VDI 6007)": "VDI_N",
        "VDI ALT (2078-1996)": "VDI_A",
        "Recknagel":           "RECK",
        "Praktiker":           "PRAK",
        "Kaltluftsee":         "KLTS",
        "KI-Hybrid":           "KI",
    }
    
    for name, (color, lw, ls) in method_colors.items():
        key = key_map[name]
        ax.plot(hours, g_sums[key], color=color, linewidth=lw, linestyle=ls, label=name)
    
    ax.set_title('METHODENVERGLEICH - SIMULTAN-TRENDKURVEN', fontweight='bold', 
                 fontsize=12, color='#3C3C3B')
    ax.set_xlabel('Tagesstunde [h]', fontsize=9)
    ax.set_ylabel('Kuhllast [W]', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper left', fontsize=8)
    ax.set_xlim(0, 23)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    return buf.getvalue()


# ==========================================
# 7. PDF REPORT: KUNDENVERSION
# ==========================================
def generate_kunden_pdf(proj, kunde, bearbeiter, firma, room_results, g_sums,
                         individual_profiles, samsung_recommendations, 
                         selected_hw, total_installed_kw):
    
    pdf = CoolMATHReport(proj, kunde, bearbeiter, firma, report_type="kunde")
    
    # --- SEITE 1: EXECUTIVE SUMMARY ---
    pdf.add_page()
    pdf.add_section_title("Executive Summary", "Klimaanlagen-Bedarfsanalyse und Systemempfehlung")
    
    peak_vdi = int(np.max(g_sums["VDI_N"]))
    peak_ki  = int(np.max(g_sums["KI"]))
    
    summary_text = (
        f"Für das Projekt '{proj}' (Auftraggeber: {kunde}) wurde eine umfassende Kühllastanalyse "
        f"nach 6 anerkannten Berechnungsverfahren durchgeführt. Die dynamische Simulation nach "
        f"VDI 6007 ermittelt einen Simultanspitzenwert von {peak_vdi:,} W ({peak_vdi/1000:.1f} kW). "
        f"Das KI-Hybrid-Modell mit prädiktiver Steuerung und Pre-Cooling-Strategie reduziert den "
        f"effektiven Leistungsbedarf auf {peak_ki:,} W ({peak_ki/1000:.1f} kW) – eine Einsparung "
        f"von {((peak_vdi - peak_ki)/peak_vdi*100):.0f}% gegenüber konventioneller Auslegung. "
        f"Die Gesamtinstallationsleistung beträgt {total_installed_kw:.2f} kW, bestehend aus "
        f"Samsung Wind-Free Comfort Wandgeräten (aktuelle Generation)."
    )
    pdf.add_info_box(summary_text, bg_rgb=(240, 248, 255))
    
    # KPI-Tabelle
    pdf.add_section_title("Kühllast-Übersicht nach Berechnungsverfahren")
    headers = ["Verfahren", "Methodik", "Peak-Last [W]", "Peak-Last [kW]", "Empfehlung"]
    widths  = [40, 55, 30, 30, 35]
    pdf.add_table_row(headers, widths, is_header=True)
    
    methods = [
        ("VDI 6007 (Neu)", "Dynamisch, TRY-Daten", int(np.max(g_sums["VDI_N"])), "★★★★★"),
        ("VDI 2078 (Alt)", "Periodisch, pauschal", int(np.max(g_sums["VDI_A"])), "★★★"),
        ("Recknagel", "Komponentenmodell", int(np.max(g_sums["RECK"])), "★★★★"),
        ("Praktiker", "Flächenheuristik", int(np.max(g_sums["PRAK"])), "★★"),
        ("Kaltluftsee", "Quelllüftung / Schichtung", int(np.max(g_sums["KLTS"])), "★★★★"),
        ("KI-Hybrid", "Prädiktiv + Pre-Cooling", int(np.max(g_sums["KI"])), "★★★★★"),
    ]
    
    for m in methods:
        row = [m[0], m[1], f"{m[2]:,}", f"{m[2]/1000:.2f}", m[3]]
        pdf.add_table_row(row, widths)
    
    total_row = ["INSTALLIERT (gesamt)", "Samsung Wind-Free WG", "—", f"{total_installed_kw:.2f}", "✓"]
    pdf.add_table_row(total_row, widths, is_total=True)
    
    # --- SEITE 2: ZONENANALYSE ---
    pdf.add_page()
    pdf.add_section_title("Zonenanalyse – Kühllast je Bereich")
    
    headers2 = ["Zone", "VDI Neu [W]", "VDI Alt [W]", "Recknagel [W]", "KI-Hybrid [W]", "Samsung"]
    widths2   = [30, 28, 28, 28, 28, 48]
    pdf.add_table_row(headers2, widths2, is_header=True)
    
    for i, r in enumerate(room_results):
        sr = samsung_recommendations[i] if i < len(samsung_recommendations) else None
        dev_str = sr["primary"]["model"] if sr and sr.get("primary") else "—"
        row = [
            r["ZONE"],
            f"{r['VDI NEU']:,}",
            f"{r['VDI ALT']:,}",
            f"{r['RECKNAGEL']:,}",
            f"{r.get('KI HYBRID', 0):,}",
            dev_str
        ]
        pdf.add_table_row(row, widths2)
    
    # --- SEITE 3: METHODENVERGLEICH-CHART ---
    pdf.add_page()
    chart_comp = make_comparison_chart(g_sums)
    pdf.add_plot(chart_comp, "Methodenvergleich – Simultane Trendkurven")
    
    # VDI Detail
    chart_vdi = make_pdf_chart(individual_profiles, g_sums["VDI_N"], 
                                "VDI 6007 – Dynamische Simulation", "vdi_n")
    pdf.add_plot(chart_vdi, "VDI 6007 Dynamisch – Einzelzonen vs. Gesamt")
    
    # --- SEITE 4: SAMSUNG EMPFEHLUNGEN ---
    pdf.add_page()
    pdf.add_section_title("Geräteempfehlung – Samsung Wind-Free Comfort", 
                          "Wandgeräte, aktuelle Generation, Wind-Free Technologie")
    
    pdf.add_info_box(
        "Alle empfohlenen Geräte sind Samsung Wind-Free Comfort Wandgeräte (AR-Serie). "
        "Die Wind-Free Technologie vermeidet direkte Kaltluftströmung durch 23.000 Mikroöffnungen "
        "und gewährleistet optimalen Komfort bei minimalem Energieverbrauch. "
        "SEER ≥ 5.8 | SCOP ≥ 3.8 | A+++ Energieklasse."
    )
    
    headers3 = ["Zone", "Modell", "Art.-Nr.", "Kühlleistung", "SEER", "Listenpreis"]
    widths3   = [28, 45, 35, 25, 15, 25]
    pdf.add_table_row(headers3, widths3, is_header=True)
    
    total_preis = 0.0
    for i, sr in enumerate(samsung_recommendations):
        if sr and sr.get("primary"):
            p = sr["primary"]
            zone = room_results[i]["ZONE"] if i < len(room_results) else f"Zone {i+1}"
            preis = p.get("preis", 0)
            total_preis += preis
            row = [
                zone,
                p.get("model", "—"),
                p.get("art_nr", "—"),
                f"{p.get('kw_class', 0):.1f} kW",
                str(p.get("seer", "—")),
                f"{preis:.0f} €"
            ]
            pdf.add_table_row(row, widths3)
    
    total3 = ["GESAMT", "", "", f"{total_installed_kw:.2f} kW", "", f"{total_preis:.0f} €"]
    pdf.add_table_row(total3, widths3, is_total=True)
    
    # --- SEITE 5: METHODIK-ERLÄUTERUNG ---
    pdf.add_page()
    pdf.add_section_title("Berechnungsverfahren – Methodik-Erläuterung")
    
    methoden_info = [
        ("1. Praktiker-Verfahren (Heuristik)", 
         "Statische Schätzung Q = A × q (60–100 W/m²). Geeignet für Vorabschätzungen, "
         "führt jedoch regelmäßig zur Überdimensionierung (+20–40%)."),
        ("2. VDI 2078 Alt (1996)",
         "Periodische Tagesgänge mit pauschalen Klimadatensätzen. Vernachlässigt individuelle "
         "Bauteilspeicher → tendenziell +15–25% höhere Lasten als VDI 6007."),
        ("3. VDI 6007 / VDI 2078 Neu (2015)",
         "Dynamische Jahressimulation mit Testreferenzjahren (TRY). Schichtweise Bauteilerfassung "
         "(RC-Modell), 72h Einschwingphase. EMPFOHLENE Auslegungsbasis."),
        ("4. Recknagel-Komponentenmodell",
         "Additive Berechnung: Q_Ges = Q_Tr + Q_St + Q_Int. Transparentes, normenkonformes "
         "Stundenprofil mit physikalisch fundierten Teillasten."),
        ("5. Kaltluftsee / Quelllüftung",
         "Reduzierung auf effektives Volumen V_eff = A × 1.8m. Lüftungseffektivität ε = 1.2–1.4. "
         "Einsparung ca. 25–30% durch Schichtungseffekt → Warmluft an Decke wird ignoriert."),
        ("6. KI-Hybrid-Modell",
         "Prädiktive Steuerung mit Phasenverschiebung (φ: 2–10h je Baumasse) und Amplitudendämpfung. "
         "Pre-Cooling in Nachtstunden (23:00–06:00) für Peak-Shaving am Nachmittag."),
    ]
    
    for title, desc in methoden_info:
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(54, 169, 225)
        pdf.cell(0, 7, pdf_safe(title), 0, 1)
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(60, 60, 59)
        pdf.multi_cell(0, 5, pdf_safe(desc))
        pdf.ln(3)
    
    return pdf_output_bytes(pdf)


# ==========================================
# 8. PDF REPORT: ÜBERGABE TECHNISCH
# ==========================================
def generate_uebergabe_pdf(proj, kunde, bearbeiter, firma, room_results, g_sums,
                            individual_profiles, samsung_recommendations,
                            selected_hw, total_installed_kw):
    
    pdf = CoolMATHReport(proj, kunde, bearbeiter, firma, report_type="simulation")
    
    # Seite 1: Vollständige Ergebnismatrix
    pdf.add_page()
    pdf.add_section_title("Vollständige Ergebnismatrix", "Alle 6 Berechnungsmethoden")
    
    headers = ["Zone", "VDI Neu", "VDI Alt", "Recknagel", "Praktiker", "Kaltl.see", "KI-Hyb."]
    widths  = [30, 24, 24, 24, 24, 24, 24]
    pdf.add_table_row(headers, widths, is_header=True)
    
    for r in room_results:
        row = [
            r["ZONE"],
            f"{r['VDI NEU']:,}",
            f"{r['VDI ALT']:,}",
            f"{r['RECKNAGEL']:,}",
            f"{r['PRAKTIKER']:,}",
            f"{r.get('KALTLUFTSEE', 0):,}",
            f"{r.get('KI HYBRID', 0):,}",
        ]
        pdf.add_table_row(row, widths)
    
    totals = [
        "SIMULTANSPITZE",
        f"{int(np.max(g_sums['VDI_N'])):,}",
        f"{int(np.max(g_sums['VDI_A'])):,}",
        f"{int(np.max(g_sums['RECK'])):,}",
        f"{int(np.max(g_sums['PRAK'])):,}",
        f"{int(np.max(g_sums['KLTS'])):,}",
        f"{int(np.max(g_sums['KI'])):,}",
    ]
    pdf.add_table_row(totals, widths, is_total=True)
    
    # Hardware
    pdf.ln(8)
    pdf.add_section_title("Hardware-Abgleich – Installierte Geräte")
    headers2 = ["Zone", "VDI Neu [W]", "Gerät", "Samsung Art.-Nr.", "Installiert [kW]"]
    widths2  = [30, 30, 45, 40, 30]
    pdf.add_table_row(headers2, widths2, is_header=True)
    
    for i, r in enumerate(room_results):
        sr = samsung_recommendations[i] if i < len(samsung_recommendations) else None
        dev = sr["primary"] if sr and sr.get("primary") else {}
        row = [
            r["ZONE"],
            f"{r['VDI NEU']:,}",
            dev.get("model", selected_hw[i] if i < len(selected_hw) else "—"),
            dev.get("art_nr", "—"),
            f"{dev.get('kw_class', selected_hw[i] if i < len(selected_hw) else 0):.1f} kW"
        ]
        pdf.add_table_row(row, widths2)
    
    total2 = ["GESAMT", "", "", "", f"{total_installed_kw:.2f} kW"]
    pdf.add_table_row(total2, widths2, is_total=True)
    
    # Seite 2: Charts
    pdf.add_page()
    chart_comp = make_comparison_chart(g_sums)
    pdf.add_plot(chart_comp, "Methodenvergleich – Alle 6 Verfahren")
    
    chart_vdi = make_pdf_chart(individual_profiles, g_sums["VDI_N"], 
                                "VDI 6007 – Einzelzonen", "vdi_n")
    pdf.add_plot(chart_vdi)
    
    # Seite 3: KI + Kaltluftsee
    pdf.add_page()
    chart_ki = make_pdf_chart(individual_profiles, g_sums["KI"], 
                               "KI-Hybrid – Peak-Shaving Effekt", "ki")
    pdf.add_plot(chart_ki)
    
    chart_kl = make_pdf_chart(individual_profiles, g_sums["KLTS"], 
                               "Kaltluftsee – Quelllüftung", "klts")
    pdf.add_plot(chart_kl)
    
    return pdf_output_bytes(pdf)


# ==========================================
# 9. MAIN APP
# ==========================================
def main():
    setup_page()
    
    # --- HEADER (Bug-freier Aufbau) ---
    col_hdr, col_logo = st.columns([4, 1])
    with col_hdr:
        st.markdown(
            '<div style="padding-top:12px; padding-left:4px; line-height:1;">'
            '<div style="display:inline-block; line-height:0.88;">'
            '<span class="cool-text">°cool</span>'
            '<span class="math-text">MATH</span>'
            '</div>'
            '<br>'
            '<span class="version-badge" style="margin-top:6px; display:inline-block;">'
            'PRO v42 &mdash; 6-METHODEN SIMULATION'
            '</span>'
            '</div>',
            unsafe_allow_html=True
        )
    with col_logo:
        logo_opts = [
            "Coolsulting_Logo_ohneHG_outlines_weiss.png",
            "Coolsulting_Logo_ohneHG_weiss.png",
        ]
        for logo in logo_opts:
            if os.path.exists(logo):
                st.image(logo, width=200)
                break
    
    st.write("---")
    
    # --- PROJEKT KONFIGURATION ---
    with st.expander("⚙️ PROJEKT-KONFIGURATION & BEARBEITER", expanded=True):
        px1, px2, px3, px4 = st.columns(4)
        proj_name  = px1.text_input("PROJEKT", "Headquarter")
        kunde_name = px2.text_input("KUNDE", "Beispiel AG")
        bearbeiter = px3.text_input("BEARBEITER", "Michael Schaepers")
        firma      = px4.text_input("FIRMA", "°coolsulting")
    
    # --- GEBÄUDE-PARAMETER ---
    st.markdown('<div class="section-header">🏢 Gebäude-Parameter</div>', unsafe_allow_html=True)
    gp1, gp2, gp3 = st.columns(3)
    bau_std = gp1.selectbox("GEBAEUDE-STANDARD", 
                             ["Altbau", "Bestand", "Neubau (GEG)", "Passivhaus"], index=0)
    bau_m   = gp2.selectbox("GEBAEUDE-MASSE", 
                             ["Schwer (Beton/Stein)", "Mittel (Ziegel/Holz-Beton)", "Leicht (Holz/Trockenbau)"], 
                             index=1)
    raumhoehe = gp3.number_input("RAUMHOEHE [m]", 2.0, 6.0, 2.5, step=0.1)
    
    # --- ZONEN KONFIGURATION ---
    st.markdown('<div class="section-header">🏠 Zonen-Konfiguration (bis 5 Räume)</div>', 
                unsafe_allow_html=True)
    
    tabs = st.tabs([f"ZONE {i+1}" for i in range(5)])
    def_ori = ["SUED", "SUED", "SUED", "SUED", "SUED"]
    
    # Ergebnis-Container
    g_sums = {k: np.zeros(24) for k in ["VDI_N", "VDI_A", "PRAK", "RECK", "KLTS", "KI"]}
    individual_profiles = []
    room_results        = []
    samsung_recs        = []
    
    for i, tab in enumerate(tabs):
        with tab:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            rc1, rc2, rc3, rc4 = st.columns(4)
            r_name  = rc1.text_input("Bezeichnung", f"Raum {i+1}", key=f"rn{i}")
            area    = rc2.number_input("Flaeche [m²]", 5.0, 500.0, 40.0, key=f"ar{i}")
            win     = rc3.number_input("Fenster [m²]", 0.0, 150.0, 2.4, key=f"wi{i}")
            orient  = rc4.selectbox("Ausrichtung", list(SOLAR_DB.keys()),
                                     index=list(SOLAR_DB.keys()).index(def_ori[i]), key=f"or{i}")
            
            rc5, rc6, rc7, rc8 = st.columns(4)
            glass   = rc5.selectbox("Glas", ["Einfach", "Doppel", "Dreifach", "Sonnenschutz"], 
                                     index=0, key=f"gl{i}")
            shade   = rc6.selectbox("Sonnenschutz", 
                                     ["Keine", "Vorhang (Innen)", "Raffstore (Aussen)", "Rollladen"], 
                                     index=1, key=f"sh{i}")
            pers    = rc7.slider("Personen", 0, 15, 2, key=f"pe{i}")
            tech    = rc8.number_input("Technik [W]", 0.0, 10000.0, 200.0, key=f"te{i}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ---- BERECHNUNGEN ----
            u, g, fc = get_phys_constants(bau_std, glass, shade)
            
            c_reck   = calc_recknagel(area, orient, bau_std, glass, shade, pers, tech, win)
            c_vdi_a  = calc_vdi_alt(c_reck)
            c_vdi_n  = calc_vdi_neu(area, orient, bau_std, glass, shade, pers, tech, win, bau_m)
            c_prak   = calc_praktiker(area, orient, bau_std, glass, shade, pers, tech)
            c_klts   = calc_kaltluftsee(area, orient, bau_std, glass, shade, pers, tech, win, bau_m, raumhoehe)
            c_ki     = calc_ki_hybrid(area, orient, bau_std, glass, shade, pers, tech, win, bau_m)
            
            # Summierung
            g_sums["RECK"]  += c_reck
            g_sums["VDI_A"] += c_vdi_a
            g_sums["VDI_N"] += c_vdi_n
            g_sums["PRAK"]  += c_prak
            g_sums["KLTS"]  += c_klts
            g_sums["KI"]    += c_ki
            
            individual_profiles.append({
                "name":  r_name,
                "reck":  c_reck,
                "vdi_a": c_vdi_a,
                "vdi_n": c_vdi_n,
                "prak":  c_prak,
                "klts":  c_klts,
                "ki":    c_ki,
            })
            
            # Samsung Empfehlung (auf Basis VDI Neu)
            peak_vdi = int(np.max(c_vdi_n))
            primary, alt = find_samsung_device(peak_vdi)
            samsung_recs.append({"zone": r_name, "primary": primary, "alt": alt, "peak_w": peak_vdi})
            
            room_results.append({
                "ZONE":       r_name,
                "VDI NEU":    peak_vdi,
                "VDI ALT":    int(np.max(c_vdi_a)),
                "RECKNAGEL":  int(np.max(c_reck)),
                "PRAKTIKER":  int(np.max(c_prak)),
                "KALTLUFTSEE":int(np.max(c_klts)),
                "KI HYBRID":  int(np.max(c_ki)),
            })
    
    # ==========================================
    # ERGEBNIS-MATRIX
    # ==========================================
    st.markdown('<div class="matrix-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="matrix-title">📊 Ergebnis-Matrix [Watt] — 6 Methoden</div>', 
                unsafe_allow_html=True)
    
    df_res = pd.DataFrame(room_results)
    totals = {
        "ZONE":         "GEBAEUDE SIMULTAN-PEAK",
        "VDI NEU":      int(np.max(g_sums["VDI_N"])),
        "VDI ALT":      int(np.max(g_sums["VDI_A"])),
        "RECKNAGEL":    int(np.max(g_sums["RECK"])),
        "PRAKTIKER":    int(np.max(g_sums["PRAK"])),
        "KALTLUFTSEE":  int(np.max(g_sums["KLTS"])),
        "KI HYBRID":    int(np.max(g_sums["KI"])),
    }
    df_res = pd.concat([df_res, pd.DataFrame([totals])], ignore_index=True)
    
    tbl = "<table class='styled-table'><thead><tr>"
    col_map = {
        "ZONE": "Zone",
        "VDI NEU": "VDI 6007 Neu",
        "VDI ALT": "VDI 2078 Alt",
        "RECKNAGEL": "Recknagel",
        "PRAKTIKER": "Praktiker",
        "KALTLUFTSEE": "Kaltluftsee",
        "KI HYBRID": "KI-Hybrid"
    }
    for col in df_res.columns:
        tbl += f"<th>{col_map.get(col, col)}</th>"
    tbl += "</tr></thead><tbody>"
    
    for _, row in df_res.iterrows():
        is_total = "SIMULTAN" in str(row["ZONE"])
        cls = " class='total-row'" if is_total else ""
        tbl += f"<tr{cls}>"
        for val in row:
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                tbl += f"<td>{val:,}</td>"
            else:
                tbl += f"<td>{val}</td>"
        tbl += "</tr>"
    tbl += "</tbody></table>"
    
    st.markdown(tbl, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ==========================================
    # SAMSUNG WIND-FREE EMPFEHLUNGEN
    # ==========================================
    st.markdown(
        '<div class="section-header">❄️ Samsung Wind-Free Wandgeräte — Geräteauslegung</div>',
        unsafe_allow_html=True
    )

    # --- Geräte je Methode berechnen ---
    method_peaks = {}
    for i in range(5):
        r = room_results[i]
        method_peaks[i] = {
            "VDI NEU":     r["VDI NEU"],
            "VDI ALT":     r["VDI ALT"],
            "RECKNAGEL":   r["RECKNAGEL"],
            "PRAKTIKER":   r["PRAKTIKER"],
            "KALTLUFTSEE": r["KALTLUFTSEE"],
            "KI HYBRID":   r["KI HYBRID"],
        }

    # Safety factor: uniform 10% for all methods per user spec
    METHOD_SAFETY = {
        "VDI NEU":     1.10,
        "VDI ALT":     1.10,
        "RECKNAGEL":   1.10,
        "PRAKTIKER":   1.10,
        "KALTLUFTSEE": 1.10,
        "KI HYBRID":   1.10,
    }

    def device_label(peak_w, safety=1.10):
        """Gibt Gerätekurzbezeichnung für Peak zurück"""
        req = (peak_w * safety) / 1000.0
        for kw in SAMSUNG_SIZES_KW:
            if kw >= req:
                d = SAMSUNG_WINDFREE_WALL[kw]
                return kw, d["model"].replace("Wind-Free Comfort ", "WF-"), d["art_nr"], d["preis"]
        kw = SAMSUNG_SIZES_KW[-1]
        d = SAMSUNG_WINDFREE_WALL[kw]
        return kw, d["model"].replace("Wind-Free Comfort ", "WF-"), d["art_nr"], d["preis"]

    # Farben je Methode
    METHOD_COLORS = {
        "VDI NEU":     ("#1a6fa8", "#e8f4fc"),
        "VDI ALT":     ("#b7770d", "#fef9e7"),
        "RECKNAGEL":   ("#3c3c3b", "#f4f4f4"),
        "PRAKTIKER":   ("#c0392b", "#fdf2f2"),
        "KALTLUFTSEE": ("#7d3c98", "#f9f0ff"),
        "KI HYBRID":   ("#1a7a5e", "#e8faf4"),
    }
    METHOD_LABELS = {
        "VDI NEU":     "VDI 6007 Neu",
        "VDI ALT":     "VDI 2078 Alt",
        "RECKNAGEL":   "Recknagel",
        "PRAKTIKER":   "Praktiker ★ OFFIZ. EMPF.",
        "KALTLUFTSEE": "Kaltluftsee",
        "KI HYBRID":   "KI-Hybrid",
    }

    zone_names = [room_results[i]["ZONE"] for i in range(5)]

    # --- Tabelle: eine Zeile je Methode ---
    st.markdown("""
    <div class="matrix-wrapper" style="padding:20px 25px;">
    <div style="font-size:13px; font-weight:900; color:#3C3C3B; text-transform:uppercase;
                letter-spacing:2px; margin-bottom:16px; border-bottom:2px solid #36A9E1;
                padding-bottom:8px;">
        Geraetevorschlag je Berechnungsmethode (Samsung Wind-Free Comfort | +10% Norm-Zuschlag)
    </div>
    """, unsafe_allow_html=True)

    # Header-Zeile
    hdr_cols = st.columns([2.2, 1, 1, 1, 1, 1])
    hdr_cols[0].markdown(
        "<div style='font-size:10px;font-weight:900;color:#3C3C3B;"
        "text-transform:uppercase;letter-spacing:1px;padding:4px 0;'>Methode</div>",
        unsafe_allow_html=True
    )
    for ci, zn in enumerate(zone_names):
        hdr_cols[ci+1].markdown(
            f"<div style='font-size:10px;font-weight:900;color:#3C3C3B;"
            f"text-transform:uppercase;letter-spacing:1px;text-align:center;"
            f"padding:4px 0;'>{zn}</div>",
            unsafe_allow_html=True
        )

    for mkey, mlabel in METHOD_LABELS.items():
        dark_color, light_color = METHOD_COLORS[mkey]
        is_official = mkey == "PRAKTIKER"

        border = f"2px solid {dark_color}" if is_official else f"1px solid {dark_color}40"
        bg     = light_color
        shadow = "box-shadow:0 2px 8px rgba(0,0,0,0.12);" if is_official else ""

        row_cols = st.columns([2.2, 1, 1, 1, 1, 1])

        # Methoden-Label
        star = " ⭐" if is_official else ""
        row_cols[0].markdown(
            f"<div style='background:{bg};border:{border};border-radius:8px;"
            f"padding:8px 10px;{shadow}margin:2px 0;'>"
            f"<div style='font-size:11px;font-weight:900;color:{dark_color};"
            f"text-transform:uppercase;letter-spacing:0.5px;'>{mlabel}{star}</div>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Gerät je Zone
        method_safety_val = METHOD_SAFETY.get(mkey, 1.10)
        for ci in range(5):
            peak_w = method_peaks[ci][mkey]
            kw, short, art_nr, preis = device_label(peak_w, safety=method_safety_val)
            row_cols[ci+1].markdown(
                f"<div style='background:{bg};border:{border};border-radius:8px;"
                f"padding:6px 8px;{shadow}margin:2px 0;text-align:center;'>"
                f"<div style='font-size:12px;font-weight:900;color:{dark_color};'>{short}</div>"
                f"<div style='font-size:10px;color:#666;margin-top:2px;'>"
                f"{kw:.1f} kW | {peak_w:,} W</div>"
                f"<div style='font-size:9px;color:#999;'>{art_nr}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # --- GRÜNE VDI-EMPFEHLUNG (restored classic style) ---
    st.markdown("""
    <div style="margin-top:24px; margin-bottom:8px;">
        <span style="font-size:12px;font-weight:900;color:rgba(255,255,255,0.8);
                     text-transform:uppercase;letter-spacing:2px;">
            VDI 6007 Empfehlung (automatisch)
        </span>
    </div>""", unsafe_allow_html=True)

    green_cols = st.columns(5)
    for i, gcol in enumerate(green_cols):
        sr = samsung_recs[i]
        primary = sr.get("primary", {}) if sr else {}
        if primary:
            gcol.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e8449,#27ae60);
                        border-radius:12px;padding:14px 12px;color:white;margin-bottom:4px;">
                <div style="font-size:9px;font-weight:800;opacity:0.85;
                            letter-spacing:1px;text-transform:uppercase;">EMPFEHLUNG VDI 6007</div>
                <div style="font-size:14px;font-weight:900;margin:4px 0;">
                    {primary.get('model','—')}</div>
                <div style="font-size:10px;opacity:0.9;line-height:1.6;">
                    📦 {primary.get('art_nr','—')}<br>
                    ❄️ {primary.get('kw_class',0):.1f} kW | SEER {primary.get('seer','—')}<br>
                    💶 {primary.get('preis',0):.0f} EUR LP
                </div>
            </div>""", unsafe_allow_html=True)

    # --- EDITIERBARE FINALE AUSWAHL ---
    st.markdown("""
    <div style="margin-top:16px; margin-bottom:8px;">
        <span style="font-size:14px;font-weight:900;color:white;text-transform:uppercase;
                     letter-spacing:2px;">✏️ Finale Geräteauswahl</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.7);margin-left:10px;">
            (editierbar — wird in JSON-Übergabe übertragen)
        </span>
    </div>
    """, unsafe_allow_html=True)

    hw_map = {
        0.0: "N.V.",
        2.0: "WF-07  |  2,0 kW  |  AR07TXFCAWKNEU  |  749 EUR",
        2.5: "WF-09  |  2,5 kW  |  AR09TXFCAWKNEU  |  849 EUR",
        3.5: "WF-12  |  3,5 kW  |  AR12TXFCAWKNEU  |  999 EUR",
        5.0: "WF-18  |  5,0 kW  |  AR18TXFCAWKNEU  |  1.299 EUR",
        6.8: "WF-24  |  6,8 kW  |  AR24TXFCAWKNEU  |  1.599 EUR",
        8.0: "WF-30  |  8,0 kW  |  AR30TXFCAWKNEU  |  1.999 EUR",
    }
    hw_keys = list(hw_map.keys())

    selected_hw = []
    final_cols = st.columns(5)

    for i, col in enumerate(final_cols):
        with col:
            r_name   = zone_names[i]
            # Default = Praktiker-Empfehlung (offizielle Empfehlung) mit 5% Safety
            prak_peak = method_peaks[i]["PRAKTIKER"]
            prak_kw, _, _, _ = device_label(prak_peak, safety=1.10)
            def_idx  = hw_keys.index(prak_kw) if prak_kw in hw_keys else 0

            # Mini-Info-Box oben
            vdi_kw, _, _, _  = device_label(method_peaks[i]["VDI NEU"],   safety=1.10)
            ki_kw,  _, _, _  = device_label(method_peaks[i]["KI HYBRID"], safety=1.10)

            st.markdown(
                f"<div style='background:rgba(255,255,255,0.12);border:1px solid "
                f"rgba(255,255,255,0.3);border-radius:10px;padding:10px;margin-bottom:6px;'>"
                f"<div style='font-size:11px;font-weight:900;color:white;"
                f"text-transform:uppercase;'>{r_name}</div>"
                f"<div style='font-size:9px;color:rgba(255,255,255,0.75);margin-top:4px;'>"
                f"VDI Neu: {vdi_kw:.1f} kW &nbsp;|&nbsp; "
                f"Praktiker: {prak_kw:.1f} kW &nbsp;|&nbsp; "
                f"KI: {ki_kw:.1f} kW"
                f"</div></div>",
                unsafe_allow_html=True
            )

            val = st.selectbox(
                f"Auswahl {r_name}",
                hw_keys,
                index=def_idx,
                key=f"hw{i}",
                format_func=lambda x, m=hw_map: m[x],
                label_visibility="collapsed"
            )
            selected_hw.append(val)

    total_kw = sum(selected_hw)
    total_preis = sum(
        SAMSUNG_WINDFREE_WALL[kw]["preis"] for kw in selected_hw if kw > 0
    )

    st.markdown(f"""
    <div class="card" style="margin-top:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:11px;font-weight:700;color:#888;
                            text-transform:uppercase;letter-spacing:1px;">
                    Installierte Gesamtleistung
                </div>
                <div style="font-size:32px;font-weight:900;color:{CI_BLUE};
                            line-height:1.1;">{total_kw:.1f} kW</div>
                <div style="font-size:11px;color:#aaa;margin-top:2px;">
                    Samsung Wind-Free Comfort | Finale Auswahl
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px;font-weight:700;color:#888;
                            text-transform:uppercase;letter-spacing:1px;">
                    Listenpreis Geräte (netto)
                </div>
                <div style="font-size:28px;font-weight:900;color:{CI_GRAY};
                            line-height:1.1;">{total_preis:,.0f} EUR</div>
                <div style="font-size:10px;color:#bbb;margin-top:2px;">
                    zzgl. MwSt. | ohne Montage &amp; Zubehör
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

        # ==========================================
    # VERGLEICHS-DIAGRAMME
    # ==========================================
    st.markdown('<div class="section-header">📈 Simultan-Trendkurven — Alle Methoden</div>',
                unsafe_allow_html=True)
    
    fig_master = go.Figure()
    
    method_traces = [
        ("PRAKTIKER (Heuristik)", g_sums["PRAK"],  "#E74C3C", 3, "dot"),
        ("VDI 6007 NEU",          g_sums["VDI_N"], "white",   5, "solid"),
        ("VDI 2078 ALT",          g_sums["VDI_A"], "#F39C12", 2.5, "dash"),
        ("RECKNAGEL",             g_sums["RECK"],  CI_GRAY,   2, "longdash"),
        ("KALTLUFTSEE",           g_sums["KLTS"],  "#9B59B6", 2.5, "dashdot"),
        ("KI-HYBRID",             g_sums["KI"],    "#1ABC9C", 3, "solid"),
    ]
    
    for name, data, color, lw, dash in method_traces:
        fig_master.add_trace(go.Scatter(
            x=HOURS, y=data, name=name,
            line=dict(width=lw, color=color, dash=dash)
        ))
    
    fig_master.update_layout(
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.05)',
        font=dict(color="white", family="Arial"),
        height=550,
        legend=dict(
            orientation="h", y=-0.15, x=0,
            bgcolor='rgba(0,0,0,0)',
            font=dict(color="white", size=11)
        ),
        xaxis=dict(
            title="Tagesstunde [h]",
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title="Kuhllast [W]",
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        margin=dict(l=60, r=20, t=20, b=80)
    )
    st.plotly_chart(fig_master, width="stretch")
    
    # --- Einzelzonen Details ---
    st.write("---")
    
    def plot_zones(mode_key, title, total_key):
        fig = go.Figure()
        zone_colors = [CI_BLUE, "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6"]
        for idx, p in enumerate(individual_profiles):
            fig.add_trace(go.Scatter(
                x=HOURS, y=p[mode_key], name=p["name"],
                line=dict(width=2, color=zone_colors[idx % len(zone_colors)], dash='dash'),
                opacity=0.8
            ))
        fig.add_trace(go.Scatter(
            x=HOURS, y=g_sums[total_key], name="GESAMT SIMULTAN",
            line=dict(width=5, color="#3C3C3B")
        ))
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='#fafafa',
            height=400,
            title=dict(text=title, font=dict(color=CI_GRAY, size=14, family='Arial Black')),
            legend=dict(orientation="h", y=-0.2, bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(title="Stunde [h]"),
            yaxis=dict(title="Kuhllast [W]"),
            margin=dict(l=60, r=20, t=50, b=80)
        )
        return fig
    
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_zones("vdi_n", "VDI 6007 - Einzelzonen", "VDI_N"), width="stretch")
    with c2:
        st.plotly_chart(plot_zones("reck", "Recknagel - Einzelzonen", "RECK"), width="stretch")
    
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_zones("klts", "Kaltluftsee / Quellueftung", "KLTS"), width="stretch")
    with c4:
        st.plotly_chart(plot_zones("ki", "KI-Hybrid (Peak-Shaving)", "KI"), width="stretch")
    
    # ==========================================
    # EXPORT SEKTION
    # ==========================================
    st.markdown('<div class="section-header">📤 Export & Berichte</div>', unsafe_allow_html=True)
    
    exp1, exp2, exp3 = st.columns(3)
    
    # 1. Übergabebericht JSON
    with exp1:
        st.markdown("""
        <div class="card-blue">
            <div style="font-size:11px; font-weight:700; opacity:0.8; margin-bottom:8px">
                🔄 ÜBERGABEBERICHT (coolMATCH)
            </div>
            <div style="font-size:12px">
                Strukturierter JSON-Datensatz für die Übergabe an coolMATCH Kalkulator.
                Enthält alle Zonen, Kühllastwerte und Geräteempfehlungen.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📋 JSON ÜBERGABEBERICHT", width="stretch"):
            transfer = build_transfer_report(
                proj_name, kunde_name, bearbeiter, firma,
                room_results, g_sums, samsung_recs, selected_hw, total_kw
            )
            json_str = json.dumps(transfer, indent=2, ensure_ascii=False)
            st.download_button(
                "⬇️ DOWNLOAD JSON",
                data=json_str.encode('utf-8'),
                file_name=f"coolMATH_Transfer_{proj_name}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                width="stretch",
                key="json_dl"
            )
    
    # 2. Technischer Übergabe-PDF
    with exp2:
        st.markdown("""
        <div class="card-blue">
            <div style="font-size:11px; font-weight:700; opacity:0.8; margin-bottom:8px">
                🔧 TECHNIKÜBERGABE PDF
            </div>
            <div style="font-size:12px">
                Vollständiger technischer Bericht mit allen 6 Methoden, Diagrammen 
                und Hardware-Abgleich für interne Übergabe.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 TECHNIKÜBERGABE GENERIEREN", width="stretch"):
            with st.spinner("⚙️ PDF wird erstellt..."):
                try:
                    pdf_bytes = generate_uebergabe_pdf(
                        proj_name, kunde_name, bearbeiter, firma,
                        room_results, g_sums, individual_profiles,
                        samsung_recs, selected_hw, total_kw
                    )
                    st.download_button(
                        "⬇️ DOWNLOAD TECHNIKÜBERGABE",
                        data=pdf_bytes,
                        file_name=f"coolMATH_Uebergabe_{proj_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        width="stretch",
                        key="pdf_tech_dl"
                    )
                    st.success("✅ Technikübergabe bereit!")
                except Exception as e:
                    st.error(f"Fehler: {e}")
    
    # 3. Kundenbericht PDF
    with exp3:
        st.markdown("""
        <div class="card-blue">
            <div style="font-size:11px; font-weight:700; opacity:0.8; margin-bottom:8px">
                👔 KUNDENBERICHT PDF
            </div>
            <div style="font-size:12px">
                Professioneller Kundenbericht mit Executive Summary, Methodenvergleich, 
                Geräteempfehlung und Methodik-Erläuterung.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📄 KUNDENBERICHT GENERIEREN", width="stretch"):
            with st.spinner("📑 Kundenbericht wird erstellt..."):
                try:
                    pdf_bytes = generate_kunden_pdf(
                        proj_name, kunde_name, bearbeiter, firma,
                        room_results, g_sums, individual_profiles,
                        samsung_recs, selected_hw, total_kw
                    )
                    st.download_button(
                        "⬇️ DOWNLOAD KUNDENBERICHT",
                        data=pdf_bytes,
                        file_name=f"coolMATH_Kundenbericht_{proj_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        width="stretch",
                        key="pdf_kd_dl"
                    )
                    st.success("✅ Kundenbericht bereit!")
                except Exception as e:
                    st.error(f"Fehler: {e}")
    
    # --- Footer ---
    st.write("---")
    st.markdown(f"""
    <div style="text-align:center; color:rgba(255,255,255,0.5); font-size:11px; padding:10px">
        °coolMATH Pro {APP_VERSION} | © {datetime.now().year} °coolsulting — Michael Schäpers<br>
        6-Methoden Kühllastsimulation | Samsung Wind-Free Integration | 
        VDI 6007 | VDI 2078 | Recknagel | Kaltluftsee | KI-Hybrid
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
