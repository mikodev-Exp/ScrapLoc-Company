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

# ==============================================================================
# CONFIGURATION AREA
# ==============================================================================
CONFIG_KECAMATAN = {
    "Tandes": {
        "alias_kec": ["tandes"],
        "kelurahan": {
            "Karangpoh": ["karangpoh", "karang poh"],
            "Balongsari": ["balongsari", "balong sari"],
            "Manukan Wetan": ["manukan wetan", "manukanwetan"],
            "Manukan Kulon": ["manukan kulon", "manukankulon"],
            "Banjar Sugihan": ["banjar sugihan", "banjarsugihan"],
            "Tandes": ["tandes", "tandes kidul", "tandes lor"]
        },
        "titik_acuan": [
            {"area": "Manukan Tama / Manukan Kulon", "lat": -7.2580, "lng": 112.6730},
            {"area": "Balongsari / Banjar Sugihan", "lat": -7.2530, "lng": 112.6620},
            {"area": "Stasiun Tandes / Karangpoh", "lat": -7.2620, "lng": 112.6880}
        ]
    },
    "Suko Manunggal": {
        "alias_kec": ["suko manunggal", "sukomanunggal"],
        "kelurahan": {
            "Putat Gede": ["putat gede", "putatgede"],
            "Sono Kwijenan": ["sono kwijenan", "sonokwijenan"],
            "Simomulyo": ["simomulyo", "simo mulyo"],
            "Suko Manunggal": ["suko manunggal", "sukomanunggal"],
            "Tanjungsari": ["tanjungsari", "tanjung sari"],
            "Simomulyo Baru": ["simomulyo baru", "simo mulyo baru"]
        },
        "titik_acuan": [
            {"area": "Suko Manunggal / Tanjungsari", "lat": -7.2650, "lng": 112.7020},
            {"area": "Simomulyo / Simo Pomahan", "lat": -7.2620, "lng": 112.7150},
            {"area": "Sono Kwijenan / HR Muhammad Utara", "lat": -7.2750, "lng": 112.6980}
        ]
    },
    "Sawahan": {
        "alias_kec": ["sawahan"],
        "kelurahan": {
            "Pakis": ["pakis"],
            "Putat Jaya": ["putat jaya", "putatjaya", "dolly"],
            "Banyu Urip": ["banyu urip", "banyuurip"],
            "Kupang Krajan": ["kupang krajan", "kupangkrajan"],
            "Petemon": ["petemon"],
            "Sawahan": ["sawahan"]
        },
        "titik_acuan": [
            {"area": "Banyu Urip / Petemon", "lat": -7.2680, "lng": 112.7240},
            {"area": "Putat Jaya / Jarak", "lat": -7.2820, "lng": 112.7230},
            {"area": "Pakis / Sawahan Utama", "lat": -7.2830, "lng": 112.7330}
        ]
    },
    "Tegalsari": {
        "alias_kec": ["tegalsari", "tegal sari"],
        "kelurahan": {
            "Keputran": ["keputran"],
            "Dr. Sutomo": ["dr. sutomo", "dr sutomo", "dokter sutomo"],
            "Tegalsari": ["tegalsari", "tegal sari"],
            "Wonorejo": ["wonorejo", "wonorejo tegalsari"],
            "Kedungdoro": ["kedungdoro", "kedung doro"]
        },
        "titik_acuan": [
            {"area": "Kedungdoro / Tegalsari Utara", "lat": -7.2630, "lng": 112.7350},
            {"area": "Dr. Sutomo / Pandegiling", "lat": -7.2800, "lng": 112.7360},
            {"area": "Keputran / Basuki Rahmat", "lat": -7.2730, "lng": 112.7440}
        ]
    },
    "Genteng": {
        "alias_kec": ["genteng"],
        "kelurahan": {
            "Embong Kaliasin": ["embong kaliasin", "embong kali asin"],
            "Ketabang": ["ketabang", "ketabang kali"],
            "Genteng": ["genteng"],
            "Peneleh": ["peneleh"],
            "Kapasari": ["kapasari", "kapas ari"]
        },
        "titik_acuan": [
            {"area": "Embong Kaliasin / Pemuda / TP", "lat": -7.2640, "lng": 112.7440},
            {"area": "Ketabang / Balai Kota Surabaya", "lat": -7.2560, "lng": 112.7480},
            {"area": "Peneleh / Kapasari / Genteng", "lat": -7.2500, "lng": 112.7430}
        ]
    }
}

# ==============================================================================
# HELPER FUNCTIONS & BOT LOGIC
# ==============================================================================
def init_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=id")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def extract_lat_lng_from_url(url):
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        return match.group(1), match.group(2)
    match_data = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if match_data:
        return match_data.group(1), match_data.group(2)
    return "", ""


def clean_text_for_matching(text):
    text = text.lower()
    text = re.sub(r"\b(kelurahan|kel\.|kel|kecamatan|kec\.|kec|desa|kota|kabupaten)\b", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return text.strip()


def is_valid_alfamidi_name(nama):
    """
    Validasi ketat nama gerai:
    - Harus diawali kata 'Alfamidi'
    - Tidak mengandung nama tenant / UMKM / Fasilitas non-gerai
    """
    nama_lower = nama.strip().lower()
    
    # 1. Harus mengandung kata 'alfamidi'
    if not nama_lower.startswith("alfamidi"):
        return False
        
    # 2. Blacklist kata-kata tenant / UMKM / ATM
    forbidden_words = [
        "kebab", "roti", "baba rafi", "john", "atm", "point coffee", 
        "point coffe", "klik alfamidi", "alfagift", "maki", "bean spot",
        "martabak", "gorengan", "es ", "depot", "warung", "stand", "laundry"
    ]
    if any(word in nama_lower for word in forbidden_words):
        return False
        
    return True


def extract_kecamatan_from_address(alamat):
    """Mengekstrak nama Kecamatan resmi dari teks alamat GMaps"""
    match = re.search(r"Kec\.\s*([^,]+)", alamat, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def parse_kelurahan_strict(alamat, dict_kelurahan):
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
# MAIN SCRAPING PROCESS
# ==============================================================================
def scrape_multi_kecamatan():
    driver = init_driver(headless=False)
    wait = WebDriverWait(driver, 15)
    semua_hasil = []

    try:
        for kec_target, kec_data in CONFIG_KECAMATAN.items():
            print(f"\n==================================================")
            print(f"  MEMPROSES KECAMATAN TARGET: {kec_target.upper()}")
            print(f"==================================================")

            data_gerai_kecamatan = {}
            dict_kelurahan = kec_data["kelurahan"]
            alias_kec_target = kec_data["alias_kec"]
            titik_acuan = kec_data["titik_acuan"]

            # FASE 1: PENJARINGAN DENGAN KATA KUNCI SKAT PER-KECAMATAN
            for idx, titik in enumerate(titik_acuan, 1):
                # PERBAIKAN UTAMA: Pencarian dispesifikkan ke Kecamatan + Surabaya
                keyword_search = f"Alfamidi {kec_target} Surabaya"
                keyword_encoded = keyword_search.replace(" ", "+")
                
                url = f"https://www.google.com/maps/search/{keyword_encoded}/@{titik['lat']},{titik['lng']},16z"
                driver.get(url)
                
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/maps/place/")]')))
                except Exception:
                    pass

                try:
                    scrollable_div = driver.find_element(By.XPATH, '//div[contains(@aria-label, "Hasil untuk")]')
                except Exception:
                    try:
                        scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
                    except Exception:
                        continue

                # Scroll secukupnya untuk area kecamatan
                for _ in range(5):
                    jumlah_awal = len(driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]'))
                    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                    
                    t0 = time.time()
                    while time.time() - t0 < 2.0:
                        jumlah_baru = len(driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]'))
                        if jumlah_baru > jumlah_awal:
                            break
                        time.sleep(0.3)

                elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/maps/place/")]')

                for elem in elements:
                    try:
                        link = elem.get_attribute("href")
                        nama = elem.get_attribute("aria-label")
                        # FILTER 1: Validasi awal nama gerai
                        if nama and is_valid_alfamidi_name(nama) and link not in data_gerai_kecamatan:
                            data_gerai_kecamatan[link] = {"nama_gerai": nama, "url_gmaps": link}
                    except Exception:
                        continue

                print(f" -> [{idx}/{len(titik_acuan)}] Area {titik['area']}: Terkumpul {len(data_gerai_kecamatan)} kandidat lokal")

            # FASE 2: DETAIL EXTRACTION & STRICT FILTERING WILAYAH
            print(f"\n --- Detail Parsing & Validasi {kec_target} ({len(data_gerai_kecamatan)} Candidate Gerai) ---")

            for idx, (link, info) in enumerate(data_gerai_kecamatan.items(), 1):
                driver.get(link)
                
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//h1 | //button[contains(@data-item-id, "address")]')))
                except Exception:
                    pass

                alamat_lengkap = ""
                selectors = [
                    '//button[contains(@data-item-id, "address")]',
                    '//button[contains(@aria-label, "Alamat")]',
                    '//button[contains(@aria-label, "Address")]',
                    '//div[contains(@class, "Io6YTe") and (contains(text(), "Surabaya") or contains(text(), "Jawa Timur"))]'
                ]

                t0 = time.time()
                while time.time() - t0 < 3.0:
                    for sel in selectors:
                        try:
                            alamat_elem = driver.find_element(By.XPATH, sel)
                            txt = alamat_elem.text.replace("Alamat: ", "").strip()
                            if txt:
                                alamat_lengkap = txt
                                break
                        except Exception:
                            continue
                    if alamat_lengkap:
                        break
                    time.sleep(0.3)

                alamat_lengkap = re.sub(r"[^\x00-\x7F]+", "", alamat_lengkap).replace("\n", " ").strip()

                # -------------------------------------------------------------
                # FILTER KETAT WILAYAH (STRICT BOUNDARY VERIFICATION)
                # -------------------------------------------------------------
                # 1. Wajib Kota Surabaya
                if "surabaya" not in alamat_lengkap.lower():
                    print(f" [{idx}/{len(data_gerai_kecamatan)}] [DISCARD] Bukan Wilayah Surabaya -> {info['nama_gerai']}")
                    continue

                # 2. Extract Kecamatan Aktual dari teks alamat
                kec_aktual = extract_kecamatan_from_address(alamat_lengkap)
                
                if kec_aktual:
                    kec_aktual_clean = clean_text_for_matching(kec_aktual)
                    is_kec_valid = any(clean_text_for_matching(alias) in kec_aktual_clean for alias in alias_kec_target)
                    if not is_kec_valid:
                        print(f" [{idx}/{len(data_gerai_kecamatan)}] [DISCARD] Beda Kecamatan ({kec_aktual} != {kec_target}) -> {info['nama_gerai']}")
                        continue

                # 3. Matching Kelurahan Strict dari Dict Target
                kel_found = parse_kelurahan_strict(alamat_lengkap, dict_kelurahan)
                if not kel_found:
                    print(f" [{idx}/{len(data_gerai_kecamatan)}] [DISCARD] Kelurahan tidak masuk target {kec_target} -> {info['nama_gerai']}")
                    continue

                # JIKA LOLOS SEMUA FILTER:
                lat, lng = extract_lat_lng_from_url(driver.current_url)
                if not lat:
                    lat, lng = extract_lat_lng_from_url(link)

                gerai_valid = {
                    "Nama Gerai": info["nama_gerai"],
                    "Alamat Lengkap": alamat_lengkap,
                    "Kecamatan": kec_target,
                    "Kelurahan": f"Kelurahan {kel_found}",
                    "Latitude": lat,
                    "Longitude": lng,
                    "URL Google Maps": driver.current_url
                }
                semua_hasil.append(gerai_valid)
                print(f" [{idx}/{len(data_gerai_kecamatan)}] [VALID 100%] {info['nama_gerai']} -> Kelurahan {kel_found}")

    finally:
        driver.quit()

    # SAVE TO CSV & DEDUPLIKASI GLOBAL
    print("\n==================================================")
    print("  FINALIASI & MENYIMPAN HASIL COMBINED")
    print("==================================================")
    if semua_hasil:
        df = pd.DataFrame(semua_hasil)
        df = df.drop_duplicates(subset=["URL Google Maps"], keep="first")

        file_output = "alfamidi_5kec_surabaya_testimoni.csv"
        df.to_csv(file_output, index=False)
        print(f"[SUCCESS] Berhasil mengumpulkan TOTAL {len(df)} gerai BENAR-BENAR VALID & BERSIH!")
        print(f"File tersimpan di: {file_output}\n")
        print(df["Kecamatan"].value_counts())
    else:
        print("[FAILED] Data kosong.")

if __name__ == "__main__":
    scrape_multi_kecamatan()