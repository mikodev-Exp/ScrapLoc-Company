import io
import threading
import time
import yaml
from yaml.loader import SafeLoader

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

from scraper import scrape, CONFIG_KECAMATAN

st.set_page_config(page_title="Scraper Google Maps", page_icon="🗺️", layout="wide")

# ==============================================================
# AUTENTIKASI
# ==============================================================
def load_credentials(path: str = "credentials.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=SafeLoader)

config = load_credentials()
authenticator = stauth.Authenticate(
    config["credentials"], config["cookie"]["name"],
    config["cookie"]["key"], config["cookie"]["expiry_days"],
)
authenticator.login(location="main")

auth_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")

if auth_status is False:
    st.error("❌ Username atau password salah.")
    st.stop()
if auth_status is None:
    st.warning("🔒 Silakan login terlebih dahulu.")
    st.stop()

with st.sidebar:
    st.success(f"✅ Login sebagai **{name}**")
    authenticator.logout(location="sidebar")
    st.divider()
    st.caption("⚠️ Proses scraping bisa memakan waktu lama. Jangan tutup halaman ini.")

# ==============================================================
# INISIALISASI GLOBAL STATE (DI LUAR SESSION_STATE)
# ==============================================================
# Menggunakan dictionary Python murni untuk komunikasi antar-thread
if "scraper_data" not in st.session_state:
    st.session_state.scraper_data = {
        "is_running": False,
        "logs": [],
        "df": None,
        "stop_event": threading.Event()
    }

data = st.session_state.scraper_data

# ==============================================================
# FUNGSI THREAD
# ==============================================================
def run_scraper_background(kecamatan, company, data_dict):
    # Callback ini dijalankan di dalam background thread.
    # JANGAN panggil st.write / st.session_state di sini!
    def progress_cb(msg):
        data_dict["logs"].append(msg)

    try:
        df = scrape(
            kecamatan_list=kecamatan,
            company_name=company,
            progress_cb=progress_cb,
            stop_event=data_dict["stop_event"]
        )
        data_dict["df"] = df
    except Exception as e:
        data_dict["logs"].append(f"❌ Error Sistem: {e}")
    finally:
        data_dict["is_running"] = False

# ==============================================================
# UI UTAMA
# ==============================================================
st.title("🗺️ Scraper Google Maps")

with st.form("form_scraping"):
    col1, col2 = st.columns([1, 2])
    with col1:
        company_name = st.text_input("Nama Perusahaan", value="alfamart")
    with col2:
        kecamatan_list = st.multiselect(
            "Pilih Kecamatan (Bisa lebih dari satu)",
            options=list(CONFIG_KECAMATAN.keys()),
            help="Pilih satu atau lebih kecamatan di Surabaya."
        )
    
    submit = st.form_submit_button("🚀 Mulai Scrape", type="primary", disabled=data["is_running"])

if submit:
    if not company_name.strip() or not kecamatan_list:
        st.error("Nama perusahaan dan kecamatan wajib diisi!")
    else:
        # Reset state
        data["is_running"] = True
        data["logs"] = ["[SISTEM] Memulai proses scraping..."]
        data["df"] = None
        data["stop_event"].clear()
        
        # Jalankan thread
        thread = threading.Thread(
            target=run_scraper_background, 
            args=(kecamatan_list, company_name.strip(), data)
        )
        thread.start()
        st.rerun() 

# ==============================================================
# AREA MONITORING (BERJALAN)
# ==============================================================
if data["is_running"]:
    st.warning("⏳ Scraping sedang berjalan di latar belakang. Silakan tunggu...")
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🛑 Hentikan Scraping", type="secondary", use_container_width=True):
            data["stop_event"].set()
            st.toast("Sinyal stop dikirim ke Chrome...")

    st.markdown("### 📝 Live Log")
    # Tampilkan log di dalam kotak kode (seperti terminal)
    log_text = "\n".join(data["logs"][-100:]) if data["logs"] else "Menunggu log dari browser..."
    st.code(log_text, language="bash")
    
    # Looping agar UI terus refresh setiap 1 detik
    time.sleep(1)
    st.rerun()

# ==============================================================
# AREA HASIL (SELESAI / BERHENTI)
# ==============================================================
elif not data["is_running"] and data["df"] is not None:
    df_hasil = data["df"]
    if not df_hasil.empty:
        st.success(f"✅ Scraping Selesai! Ditemukan {len(df_hasil)} gerai.")
        st.dataframe(df_hasil, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_hasil.to_excel(writer, index=False, sheet_name="Hasil")
        buffer.seek(0)
        
        safe_company = "".join(c if c.isalnum() else "_" for c in company_name.strip())
        st.download_button(
            label="⬇️ Download Excel (.xlsx)",
            data=buffer,
            file_name=f"{safe_company}_hasil_scraping.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    else:
        st.info("Proses selesai. Tidak ada gerai yang ditemukan atau proses dihentikan.")