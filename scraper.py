import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# ==============================================================================
# CONFIGURATION AREA (31 KECAMATAN SURABAYA)
# ==============================================================================
CONFIG_KECAMATAN = {
    "Tandes": {
        "alias_kec": ["tandes"], "kelurahan": {"Karangpoh": ["karangpoh", "karang poh"], "Balongsari": ["balongsari", "balong sari"], "Manukan Wetan": ["manukan wetan", "manukanwetan"], "Manukan Kulon": ["manukan kulon", "manukankulon"], "Banjar Sugihan": ["banjar sugihan", "banjarsugihan"], "Tandes": ["tandes", "tandes kidul", "tandes lor"]},
        "titik_acuan": [{"area": "Manukan", "lat": -7.2580, "lng": 112.6730}, {"area": "Balongsari", "lat": -7.2530, "lng": 112.6620}, {"area": "Karangpoh", "lat": -7.2620, "lng": 112.6880}]
    },
    "Suko Manunggal": {
        "alias_kec": ["suko manunggal", "sukomanunggal"], "kelurahan": {"Putat Gede": ["putat gede", "putatgede"], "Sono Kwijenan": ["sono kwijenan", "sonokwijenan"], "Simomulyo": ["simomulyo", "simo mulyo"], "Suko Manunggal": ["suko manunggal", "sukomanunggal"], "Tanjungsari": ["tanjungsari", "tanjung sari"], "Simomulyo Baru": ["simomulyo baru", "simo mulyo baru"]},
        "titik_acuan": [{"area": "Tanjungsari", "lat": -7.2650, "lng": 112.7020}, {"area": "Simomulyo", "lat": -7.2620, "lng": 112.7150}, {"area": "Kwijenan", "lat": -7.2750, "lng": 112.6980}]
    },
    "Sawahan": {
        "alias_kec": ["sawahan"], "kelurahan": {"Pakis": ["pakis"], "Putat Jaya": ["putat jaya", "putatjaya", "dolly"], "Banyu Urip": ["banyu urip", "banyuurip"], "Kupang Krajan": ["kupang krajan", "kupangkrajan"], "Petemon": ["petemon"], "Sawahan": ["sawahan"]},
        "titik_acuan": [{"area": "Banyu Urip", "lat": -7.2680, "lng": 112.7240}, {"area": "Putat Jaya", "lat": -7.2820, "lng": 112.7230}, {"area": "Pakis", "lat": -7.2830, "lng": 112.7330}]
    },
    "Tegalsari": {
        "alias_kec": ["tegalsari", "tegal sari"], "kelurahan": {"Keputran": ["keputran"], "Dr. Sutomo": ["dr. sutomo", "dr sutomo", "dokter sutomo"], "Tegalsari": ["tegalsari", "tegal sari"], "Wonorejo": ["wonorejo", "wonorejo tegalsari"], "Kedungdoro": ["kedungdoro", "kedung doro"]},
        "titik_acuan": [{"area": "Kedungdoro", "lat": -7.2630, "lng": 112.7350}, {"area": "Dr. Sutomo", "lat": -7.2800, "lng": 112.7360}, {"area": "Keputran", "lat": -7.2730, "lng": 112.7440}]
    },
    "Genteng": {
        "alias_kec": ["genteng"], "kelurahan": {"Embong Kaliasin": ["embong kaliasin", "embong kali asin"], "Ketabang": ["ketabang", "ketabang kali"], "Genteng": ["genteng"], "Peneleh": ["peneleh"], "Kapasari": ["kapasari", "kapas ari"]},
        "titik_acuan": [{"area": "Embong Kaliasin", "lat": -7.2640, "lng": 112.7440}, {"area": "Ketabang", "lat": -7.2560, "lng": 112.7480}, {"area": "Peneleh", "lat": -7.2500, "lng": 112.7430}]
    },
    "Asemrowo": {"alias_kec": ["asemrowo"], "kelurahan": {}, "titik_acuan": [{"area": "Asemrowo", "lat": -7.2350, "lng": 112.6880}]},
    "Benowo": {"alias_kec": ["benowo"], "kelurahan": {}, "titik_acuan": [{"area": "Benowo", "lat": -7.2360, "lng": 112.6300}]},
    "Bubutan": {"alias_kec": ["bubutan"], "kelurahan": {}, "titik_acuan": [{"area": "Bubutan", "lat": -7.2480, "lng": 112.7380}]},
    "Bulak": {"alias_kec": ["bulak"], "kelurahan": {}, "titik_acuan": [{"area": "Bulak", "lat": -7.2350, "lng": 112.7800}]},
    "Dukuh Pakis": {"alias_kec": ["dukuh pakis", "dukuhpakis"], "kelurahan": {}, "titik_acuan": [{"area": "Dukuh Pakis", "lat": -7.2800, "lng": 112.7100}]},
    "Gayungan": {"alias_kec": ["gayungan"], "kelurahan": {}, "titik_acuan": [{"area": "Gayungan", "lat": -7.3300, "lng": 112.7200}]},
    "Gubeng": {"alias_kec": ["gubeng"], "kelurahan": {}, "titik_acuan": [{"area": "Gubeng", "lat": -7.2700, "lng": 112.7500}]},
    "Gunung Anyar": {"alias_kec": ["gunung anyar", "gununganyar"], "kelurahan": {}, "titik_acuan": [{"area": "Gunung Anyar", "lat": -7.3400, "lng": 112.7900}]},
    "Jambangan": {"alias_kec": ["jambangan"], "kelurahan": {}, "titik_acuan": [{"area": "Jambangan", "lat": -7.3200, "lng": 112.7100}]},
    "Karang Pilang": {"alias_kec": ["karang pilang", "karangpilang"], "kelurahan": {}, "titik_acuan": [{"area": "Karang Pilang", "lat": -7.3300, "lng": 112.6900}]},
    "Kenjeran": {"alias_kec": ["kenjeran"], "kelurahan": {}, "titik_acuan": [{"area": "Kenjeran", "lat": -7.2300, "lng": 112.7700}]},
    "Krembangan": {"alias_kec": ["krembangan"], "kelurahan": {}, "titik_acuan": [{"area": "Krembangan", "lat": -7.2300, "lng": 112.7200}]},
    "Lakarsantri": {"alias_kec": ["lakarsantri"], "kelurahan": {}, "titik_acuan": [{"area": "Lakarsantri", "lat": -7.3100, "lng": 112.6500}]},
    "Mulyorejo": {"alias_kec": ["mulyorejo"], "kelurahan": {}, "titik_acuan": [{"area": "Mulyorejo", "lat": -7.2600, "lng": 112.7800}]},
    "Pabean Cantian": {"alias_kec": ["pabean cantian", "pabeancantian"], "kelurahan": {}, "titik_acuan": [{"area": "Pabean Cantian", "lat": -7.2200, "lng": 112.7300}]},
    "Pakal": {"alias_kec": ["pakal"], "kelurahan": {}, "titik_acuan": [{"area": "Pakal", "lat": -7.2400, "lng": 112.6100}]},
    "Rungkut": {"alias_kec": ["rungkut"], "kelurahan": {}, "titik_acuan": [{"area": "Rungkut", "lat": -7.3200, "lng": 112.7800}]},
    "Sambikerep": {"alias_kec": ["sambikerep"], "kelurahan": {}, "titik_acuan": [{"area": "Sambikerep", "lat": -7.2800, "lng": 112.6400}]},
    "Semampir": {"alias_kec": ["semampir"], "kelurahan": {}, "titik_acuan": [{"area": "Semampir", "lat": -7.2100, "lng": 112.7400}]},
    "Simokerto": {"alias_kec": ["simokerto"], "kelurahan": {}, "titik_acuan": [{"area": "Simokerto", "lat": -7.2400, "lng": 112.7500}]},
    "Sukolilo": {"alias_kec": ["sukolilo"], "kelurahan": {}, "titik_acuan": [{"area": "Sukolilo", "lat": -7.2800, "lng": 112.7900}]},
    "Tambaksari": {"alias_kec": ["tambaksari"], "kelurahan": {}, "titik_acuan": [{"area": "Tambaksari", "lat": -7.2500, "lng": 112.7600}]},
    "Tenggilis Mejoyo": {"alias_kec": ["tenggilis mejoyo", "tenggilismejoyo"], "kelurahan": {}, "titik_acuan": [{"area": "Tenggilis Mejoyo", "lat": -7.3100, "lng": 112.7600}]},
    "Wiyung": {"alias_kec": ["wiyung"], "kelurahan": {}, "titik_acuan": [{"area": "Wiyung", "lat": -7.3100, "lng": 112.6800}]},
    "Wonocolo": {"alias_kec": ["wonocolo"], "kelurahan": {}, "titik_acuan": [{"area": "Wonocolo", "lat": -7.3100, "lng": 112.7300}]},
    "Wonokromo": {"alias_kec": ["wonokromo"], "kelurahan": {}, "titik_acuan": [{"area": "Wonokromo", "lat": -7.2900, "lng": 112.7400}]}
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=id")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Mencegah Selenium menunggu terlalu lama saat halaman Google Maps lambat dimuat
    options.page_load_strategy = 'eager' 
    
    if os.name == "posix":
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    else:
        service = Service(ChromeDriverManager().install())
        
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30) # Batas waktu buka halaman 30 detik
    return driver

def extract_lat_lng_from_url(url):
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match: return match.group(1), match.group(2)
    match_data = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if match_data: return match_data.group(1), match_data.group(2)
    return "", ""

def clean_text_for_matching(text):
    text = text.lower()
    text = re.sub(r"\b(kelurahan|kel\.|kel|kecamatan|kec\.|kec|desa|kota|kabupaten)\b", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return text.strip()

def is_valid_company_name(nama, company_name):
    nama_lower = nama.strip().lower()
    if not nama_lower.startswith(company_name.strip().lower()): return False
    forbidden_words = ["kebab", "roti", "baba rafi", "john", "atm", "point coffee", "point coffe", "klik", "alfagift", "maki", "bean spot", "martabak", "gorengan", "depot", "warung", "stand", "laundry"]
    if any(word in nama_lower for word in forbidden_words): return False
    return True

def extract_kecamatan_from_address(alamat):
    match = re.search(r"Kec\.\s*([^,]+)", alamat, re.IGNORECASE)
    if match: return match.group(1).strip()
    return None

def parse_kelurahan_strict(alamat, dict_kelurahan):
    if not dict_kelurahan: return "Tidak Spesifik"
    alamat_clean = clean_text_for_matching(alamat)
    alamat_no_space = re.sub(r"\s+", "", alamat_clean)
    for kel_std, alias_list in dict_kelurahan.items():
        for alias in alias_list:
            alias_clean = clean_text_for_matching(alias)
            alias_no_space = re.sub(r"\s+", "", alias_clean)
            if alias_clean in alamat_clean or alias_no_space in alamat_no_space:
                return kel_std
    return None

# ==============================================================================
# MAIN SCRAPING FUNCTION
# ==============================================================================
def scrape(kecamatan_list, company_name, progress_cb=None, stop_event=None):
    def log(msg):
        if progress_cb: progress_cb(msg)

    driver = init_driver()
    wait = WebDriverWait(driver, 15)
    semua_hasil = []

    try:
        for k_idx, kec_target in enumerate(kecamatan_list, 1):
            if stop_event and stop_event.is_set():
                log("🛑 Proses dihentikan oleh pengguna.")
                break

            kec_data = CONFIG_KECAMATAN.get(kec_target)
            if not kec_data: continue

            log(f"\n[{k_idx}/{len(kecamatan_list)}] 🚀 Memproses kecamatan: {kec_target}")
            data_gerai_kecamatan = {}
            dict_kelurahan = kec_data["kelurahan"]
            alias_kec_target = kec_data["alias_kec"]
            titik_acuan = kec_data["titik_acuan"]

            # FASE 1: PENJARINGAN
            for idx, titik in enumerate(titik_acuan, 1):
                if stop_event and stop_event.is_set(): break
                
                keyword_search = f"{company_name} {kec_target} Surabaya".replace(" ", "+")
                url = f"https://www.google.com/maps/search/{keyword_search}/@{titik['lat']},{titik['lng']},16z"
                log(f"  🔍 [{kec_target}] Mencari di area: {titik['area']}...")
                
                try:
                    driver.get(url)
                except Exception as e:
                    log(f"  ⚠️ Timeout saat membuka area {titik['area']}. Lanjut ke area berikutnya.")
                    continue

                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/maps/place/")]')))
                except Exception: 
                    log(f"  ⚠️ Tidak ada hasil ditemukan di area {titik['area']}.")
                    continue

                try:
                    scrollable_div = driver.find_element(By.XPATH, '//div[contains(@aria-label, "Hasil untuk")]')
                except Exception:
                    try: scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
                    except Exception: continue

                # Scroll
                for _ in range(3): # Dikurangi jadi 3x agar tidak terlalu lama
                    if stop_event and stop_event.is_set(): break
                    jumlah_awal = len(driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]'))
                    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                    time.sleep(1.5)

                elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]')
                for elem in elements:
                    try:
                        link = elem.get_attribute("href")
                        nama = elem.get_attribute("aria-label")
                        if (nama and is_valid_company_name(nama, company_name) and link not in data_gerai_kecamatan):
                            data_gerai_kecamatan[link] = {"nama_gerai": nama, "url_gmaps": link}
                    except Exception: continue

                log(f"  📌 [{kec_target}] Area {idx}/{len(titik_acuan)}: Total {len(data_gerai_kecamatan)} kandidat gerai.")

            # FASE 2: VALIDASI
            log(f"  ⏳ Memeriksa alamat detail untuk {len(data_gerai_kecamatan)} kandidat...")
            for idx, (link, info) in enumerate(data_gerai_kecamatan.items(), 1):
                if stop_event and stop_event.is_set(): break
                
                log(f"    🔎 ({idx}/{len(data_gerai_kecamatan)}) Cek: {info['nama_gerai']}")
                try:
                    driver.get(link)
                except Exception:
                    log(f"    ⚠️ Gagal membuka detail {info['nama_gerai']}.")
                    continue

                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//h1 | //button[contains(@data-item-id, "address")]')))
                except Exception: pass

                alamat_lengkap = ""
                selectors = ['//button[contains(@data-item-id, "address")]', '//button[contains(@aria-label, "Alamat")]', '//button[contains(@aria-label, "Address")]', '//div[contains(@class, "Io6YTe") and (contains(text(), "Surabaya") or contains(text(), "Jawa Timur"))]']
                
                t0 = time.time()
                while time.time() - t0 < 2.0:
                    for sel in selectors:
                        try:
                            txt = driver.find_element(By.XPATH, sel).text.replace("Alamat: ", "").strip()
                            if txt: alamat_lengkap = txt; break
                        except Exception: continue
                    if alamat_lengkap: break
                    time.sleep(0.2)

                alamat_lengkap = re.sub(r"[^\x00-\x7F]+", "", alamat_lengkap).replace("\n", " ").strip()

                if "surabaya" not in alamat_lengkap.lower(): 
                    log(f"      ❌ Ditolak: Bukan Surabaya.")
                    continue

                kec_aktual = extract_kecamatan_from_address(alamat_lengkap)
                if kec_aktual:
                    if not any(clean_text_for_matching(alias) in clean_text_for_matching(kec_aktual) for alias in alias_kec_target): 
                        log(f"      ❌ Ditolak: Beda Kecamatan ({kec_aktual}).")
                        continue

                kel_found = parse_kelurahan_strict(alamat_lengkap, dict_kelurahan)
                if not kel_found: 
                    log(f"      ❌ Ditolak: Kelurahan tidak masuk target.")
                    continue

                lat, lng = extract_lat_lng_from_url(driver.current_url)
                if not lat: lat, lng = extract_lat_lng_from_url(link)

                semua_hasil.append({
                    "Nama Gerai": info["nama_gerai"], "Alamat Lengkap": alamat_lengkap,
                    "Kecamatan": kec_target, "Kelurahan": kel_found,
                    "Latitude": lat, "Longitude": lng, "URL Google Maps": driver.current_url
                })
                log(f"      ✅ VALID: {info['nama_gerai']}")
                
    except Exception as e:
        log(f"⚠️ Error sistem: {e}")
    finally:
        driver.quit()

    df = pd.DataFrame(semua_hasil)
    if not df.empty:
        df = df.drop_duplicates(subset=["URL Google Maps"], keep="first")
    return df