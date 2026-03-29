import customtkinter as ctk
import threading
import time
import re
import imaplib
import email
import email.utils
from datetime import datetime, timedelta, timezone
import random
import os
import json
import sys
import winsound
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

DEFAULT_URL = "any link or application"

class BotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("bot")
        self.geometry("700x1100") 
        self.resizable(False, False)
        
        self.drivers = []

        try:
            if os.path.exists("logo.png"):
                bg_image_data = Image.open("logo.png")
                bg_image_resized = bg_image_data.resize((700, 1100), Image.LANCZOS)
                self.bg_image = ctk.CTkImage(light_image=bg_image_resized, dark_image=bg_image_resized, size=(700, 1100))
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()
        except:
            pass

        self.veri_havuzu = {
            "Site 1": { "url": DEFAULT_URL, "hesaplar": {f"Hesap {i}": {"user": "", "pass": "", "gmail": "", "gmail_pass": ""} for i in range(1, 151)}, "secili_hesap": "Hesap 1", "proxies": "" },
            "Site 2": { "url": DEFAULT_URL, "hesaplar": {f"Hesap {i}": {"user": "", "pass": "", "gmail": "", "gmail_pass": ""} for i in range(1, 151)}, "secili_hesap": "Hesap 1", "proxies": "" },
            "Site 3": { "url": DEFAULT_URL, "hesaplar": {f"Hesap {i}": {"user": "", "pass": "", "gmail": "", "gmail_pass": ""} for i in range(1, 151)}, "secili_hesap": "Hesap 1", "proxies": "" }
        }
        self.aktif_site = "Site 1"
        self.aktif_hesap = "Hesap 1"

        self.tabview = ctk.CTkTabview(self, width=650, height=950)
        self.tabview.pack(pady=10, padx=10)
        
        self.tab_giris = self.tabview.add("Giriş İşlemleri")
        self.tab_proxy = self.tabview.add("Proxy Ayarları")
        

        self.site_selector = ctk.CTkSegmentedButton(self.tab_giris, values=["Site 1", "Site 2", "Site 3"], command=self.site_degistir)
        self.site_selector.set("Site 1"); self.site_selector.pack(pady=5)
        
        self.entry_url = ctk.CTkEntry(self.tab_giris, placeholder_text="Giriş Linki", width=500); self.entry_url.pack(pady=2)
        
        self.account_selector = ctk.CTkComboBox(self.tab_giris, values=[f"Hesap {i}" for i in range(1,151)], command=self.hesap_degistir, width=200)
        self.account_selector.set("Hesap 1"); self.account_selector.pack(pady=5)
        
        ctk.CTkLabel(self.tab_giris, text="Kullanıcı Adı:").pack(); self.entry_user = ctk.CTkEntry(self.tab_giris, width=400); self.entry_user.pack()
        ctk.CTkLabel(self.tab_giris, text="Şifre:").pack(); self.entry_pass = ctk.CTkEntry(self.tab_giris, show="*", width=400); self.entry_pass.pack()
        ctk.CTkLabel(self.tab_giris, text="Gmail:").pack(); self.entry_gmail = ctk.CTkEntry(self.tab_giris, width=400); self.entry_gmail.pack()
        ctk.CTkLabel(self.tab_giris, text="Gmail Şifre:").pack(); self.entry_gmail_pass = ctk.CTkEntry(self.tab_giris, show="*", width=400); self.entry_gmail_pass.pack()
        
        ctk.CTkLabel(self.tab_giris, text="Proxy Değişim Modu:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        self.proxy_mode_selector = ctk.CTkSegmentedButton(self.tab_giris, values=["Normal (5 Hesapta 1)", "Yoğun (3 Hesapta 1)"])
        self.proxy_mode_selector.set("Normal (5 Hesapta 1)")
        self.proxy_mode_selector.pack(pady=5)


        self.btn_save = ctk.CTkButton(self.tab_giris, text="Kaydet", command=self.manuel_kaydet); self.btn_save.pack(pady=5)
        self.btn_start = ctk.CTkButton(self.tab_giris, text="Tekli Başlat", command=self.baslat_tekli); self.btn_start.pack(pady=5)
        self.btn_bulk = ctk.CTkButton(self.tab_giris, text="SIRALI BAŞLAT", command=self.baslat_toplu, fg_color="green"); self.btn_bulk.pack(pady=5)
        
        self.textbox_proxies = ctk.CTkTextbox(self.tab_proxy, width=500, height=400); self.textbox_proxies.pack(pady=10)
        self.btn_save_proxy = ctk.CTkButton(self.tab_proxy, text="Kaydet", command=self.manuel_kaydet); self.btn_save_proxy.pack()
        
        self.log_box = ctk.CTkTextbox(self, width=650, height=100); self.log_box.pack(pady=10)
        
        self.db_yukle(); self.ekrani_guncelle(); self.protocol("WM_DELETE_WINDOW", self.kapatirken_kaydet)

        threading.Thread(target=self.session_koruyucu, daemon=True).start()

    def session_koruyucu(self):
        while True:
            time.sleep(900)
            if self.drivers:
                self.log_yaz("[OTO-REFRESH] 15 dk doldu, sayfalar yenileniyor...")
                for driver in self.drivers:
                    try:
                        current = driver.current_url
                        driver.get(current)
                        time.sleep(1)
                    except:
                        pass
                self.log_yaz("Tüm sekmeler tazelendi.")
    def db_yukle(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.veri_havuzu = data.get("veri_havuzu", self.veri_havuzu)
            except: pass
    def db_kaydet(self):
        self.verileri_hafizaya_cek()
        save_data = {"veri_havuzu": self.veri_havuzu, "aktif_site": self.aktif_site, "aktif_hesap": self.aktif_hesap}
        try:
            with open("settings.json", "w", encoding="utf-8") as f: json.dump(save_data, f, indent=4)
        except: pass
    def kapatirken_kaydet(self): self.db_kaydet(); self.destroy(); sys.exit()
    def verileri_hafizaya_cek(self):
        if self.aktif_site not in self.veri_havuzu: self.veri_havuzu[self.aktif_site] = {"url": DEFAULT_URL, "hesaplar": {}, "proxies": ""}
        self.veri_havuzu[self.aktif_site]["url"] = self.entry_url.get()
        self.veri_havuzu[self.aktif_site]["proxies"] = self.textbox_proxies.get("1.0", "end-1c")
        self.veri_havuzu[self.aktif_site]["hesaplar"][self.aktif_hesap] = {"user": self.entry_user.get(), "pass": self.entry_pass.get(), "gmail": self.entry_gmail.get(), "gmail_pass": self.entry_gmail_pass.get()}
    def ekrani_guncelle(self):
        site_data = self.veri_havuzu.get(self.aktif_site, {"url": DEFAULT_URL, "hesaplar": {}, "proxies": ""})
        hesap_data = site_data["hesaplar"].get(self.aktif_hesap, {"user": "", "pass": "", "gmail": "", "gmail_pass": ""})
        self.entry_url.delete(0, "end"); self.entry_url.insert(0, site_data.get("url", DEFAULT_URL))
        self.textbox_proxies.delete("1.0", "end"); self.textbox_proxies.insert("1.0", site_data.get("proxies", ""))
        self.entry_user.delete(0, "end"); self.entry_user.insert(0, hesap_data["user"])
        self.entry_pass.delete(0, "end"); self.entry_pass.insert(0, hesap_data["pass"])
        self.entry_gmail.delete(0, "end"); self.entry_gmail.insert(0, hesap_data["gmail"])
        self.entry_gmail_pass.delete(0, "end"); self.entry_gmail_pass.insert(0, hesap_data["gmail_pass"])
    def site_degistir(self, val): self.verileri_hafizaya_cek(); self.aktif_site = val; self.account_selector.set("Hesap 1"); self.aktif_hesap = "Hesap 1"; self.ekrani_guncelle()
    def hesap_degistir(self, val): self.verileri_hafizaya_cek(); self.aktif_hesap = val; self.ekrani_guncelle()
    def manuel_kaydet(self): self.db_kaydet(); self.log_yaz(f"Kaydedildi.")
    def log_yaz(self, msg): self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n"); self.log_box.see("end")

    def js_tikla(self, driver, element): 
        try: 
            driver.execute_script("arguments[0].click();", element)
            return True 
        except: 
            return False

    def human_type(self, element, text):
        try:
            element.click()
            time.sleep(0.2)
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.20))
            return True
        except:
            return False

    def js_yaz(self, driver, element, text):
        try: 
            driver.execute_script(f"arguments[0].value = '{text}';", element)
            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));")
            return True
        except: 
            return False

    def html_temizle(self, text): return re.sub(r'<[^>]+>', ' ', text).strip()

    def kod_cek(self, g, p):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(g, p)
            mail.select("inbox")
            status, messages = mail.search(None, "ALL")
            mail_ids = messages[0].split()
            if not mail_ids: mail.logout(); return None
            
            son_mailler = reversed(mail_ids[-3:])
            
            for mail_id in son_mailler:
                try:
                    res, msg_data = mail.fetch(str(mail_id.decode()), "(RFC822)")
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    mail_date_str = msg.get("Date")
                    if mail_date_str:
                        mail_date = email.utils.parsedate_to_datetime(mail_date_str)
                        if mail_date.tzinfo: mail_date = mail_date.astimezone(timezone.utc)
                        now = datetime.now(timezone.utc)
                        if (now - mail_date).total_seconds() > 120: continue 
                    
                    raw_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ["text/plain", "text/html"]:
                                try: raw_body += part.get_payload(decode=True).decode(errors="ignore") + " "
                                except: pass
                    else:
                        try: raw_body = msg.get_payload(decode=True).decode(errors="ignore")
                        except: pass
                    
                    temiz_metin = self.html_temizle(raw_body)
                    tum_kodlar = re.findall(r'\b\d{6}\b', temiz_metin)
                    
                    for kod in tum_kodlar:
                        if kod == "320539" or kod == "000000": continue
                        mail.logout(); return kod
                except: continue
            mail.logout()
        except: pass
        return None

    def captcha_kontrol(self, driver):
        if "captcha" in driver.page_source.lower() or "güvenlik" in driver.page_source.lower():
            try:
                captcha_elem = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')] | //iframe[contains(@src, 'recaptcha')]")
                if captcha_elem.is_displayed():
                    self.log_yaz("⚠ CAPTCHA ÇIKTI! Manuel çözün...")
                    for _ in range(5):
                        try: winsound.Beep(1000, 300)
                        except: pass
                        time.sleep(0.1)
                    
                    max_bekleme = 60
                    while max_bekleme > 0:
                        try: 
                            if not captcha_elem.is_displayed(): return True
                        except: return True
                        time.sleep(1); max_bekleme -= 1
            except: pass
        return False

    def mail_test_et(self):
        self.verileri_hafizaya_cek()
        data = self.veri_havuzu[self.aktif_site]["hesaplar"][self.aktif_hesap]
        def worker():
            try:
                m = imaplib.IMAP4_SSL("imap.gmail.com")
                m.login(data["gmail"], data["gmail_pass"])
                m.logout()
                self.log_yaz("Gmail bağlantısı BAŞARILI!")
            except Exception as e: self.log_yaz(f"Gmail hatası: {e}")
        threading.Thread(target=worker).start()

    def baslat_tekli(self):
        self.verileri_hafizaya_cek(); self.db_kaydet()
        proxies = self.veri_havuzu[self.aktif_site]["proxies"].strip().split("\n")
        proxy = proxies[0].strip().split(':')[0] + ":" + proxies[0].strip().split(':')[1] if proxies and proxies[0].strip() else None
        t = threading.Thread(target=self.botu_calistir, args=(self.entry_url.get(), self.veri_havuzu[self.aktif_site]["hesaplar"][self.aktif_hesap], proxy, False))
        t.start()

    def baslat_toplu(self):
        self.verileri_hafizaya_cek(); self.db_kaydet()

        secilen_mod = self.proxy_mode_selector.get()
        if "3 Hesapta" in secilen_mod:
            limit = 3
            self.log_yaz("YOĞUN MOD AKTİF: 3 hesapta 1 proxy değişecek.")
        else:
            limit = 5
            self.log_yaz("NORMAL MOD AKTİF: 5 hesapta 1 proxy değişecek.")

        def toplu_worker():
            self.btn_bulk.configure(state="disabled", text="Sıralı İşlem Sürüyor...")
            site_data = self.veri_havuzu[self.aktif_site]
            url = site_data["url"]
            proxies = [p.strip() for p in site_data["proxies"].strip().split("\n") if p.strip()]
            
            hesap_sayaci = 0
            proxy_cursor = 0 
            current_proxy_usage = 0 
            
            for i in range(1, 151):
                hesap_adi = f"Hesap {i}"
                hesap_data = site_data["hesaplar"].get(hesap_adi)
                if not hesap_data or not hesap_data["user"]: continue
                
                hesap_sayaci += 1

                secilen_proxy = None
                if proxies:
                    current_proxy_usage += 1
                    if current_proxy_usage > limit:
                        proxy_cursor += 1
                        current_proxy_usage = 1 
                        
                    secilen_proxy = proxies[proxy_cursor % len(proxies)]
                
                self.log_yaz(f"\n--- {hesap_adi} BAŞLATILIYOR ---")
                if secilen_proxy: 
                    try: ip_goster = secilen_proxy.split(':')[0]
                    except: ip_goster = "Bilinmiyor"
                    self.log_yaz(f"🛡 Proxy: {ip_goster} (Sıra: {current_proxy_usage}/{limit})")
                
                self.botu_calistir(url, hesap_data, secilen_proxy, False)
                self.log_yaz(f"{hesap_adi} bitti. 1.5sn bekleme...")
                time.sleep(1.5)
                
            self.log_yaz(f"\nTÜM İŞLEMLER BİTTİ!")
            winsound.Beep(500, 1000)
            self.btn_bulk.configure(state="normal", text="SIRALI BAŞLAT")
        t = threading.Thread(target=toplu_worker)
        t.start()

    def botu_calistir(self, url, data, proxy_string=None, close_on_finish=False):
        opt = webdriver.ChromeOptions()
        opt.page_load_strategy = 'eager' 
        
        opt.add_argument("--start-maximized")
        opt.add_argument("--disable-notifications")
        if proxy_string: opt.add_argument(f'--proxy-server={proxy_string}')
        
        prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
        opt.add_experimental_option("prefs", prefs)
        opt.add_experimental_option("excludeSwitches", ["enable-automation"])
        opt.add_experimental_option('useAutomationExtension', False)
        
        driver = None
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)
            self.drivers.append(driver) 
            wait = WebDriverWait(driver, 30)
        except Exception as e: self.log_yaz(f"Driver Hatası: {e}"); return

        try:
            try:
                driver.get("check ip")
                time.sleep(0.5) 
                ip = driver.find_element(By.TAG_NAME, "body").text.strip()
                self.log_yaz(f"IP: {ip}")
            except: pass

            driver.get(url)
            self.log_yaz("Siteye girildi. 5 sn bekleniyor (İnsan modu)...")
            time.sleep(5) 

            try:
                popups = driver.find_elements(By.XPATH, "//*[contains(@class, 'close') or text()='X' or text()='x' or contains(text(), 'Kapat')]")
                for p in popups:
                    if p.is_displayed(): self.js_tikla(driver, p); time.sleep(0.5)
            except: pass

            self.log_yaz("Giriş butonu aranıyor...")
            giris_tiklandi = False
            
            selectors = [
                "//a[contains(@class, 'login')]", 
                "//a[contains(@href, 'login')]", 
                "//*[contains(text(), 'GİRİŞ')]", 
                "//*[contains(text(), 'Giriş')]",
                "//*[contains(text(), 'Login')]",
                "//div[contains(@class, 'login-btn')]", 
                "//header//button", 
                "//a[normalize-space()='GİRİŞ']", 
                "//*[@id='login-btn']",
                "//button[contains(@class, 'btn') and contains(@class, 'primary')]"
            ]
            
            for sel in selectors:
                try:
                    btns = driver.find_elements(By.XPATH, sel)
                    for btn in btns:
                        if btn.is_displayed():
                            self.js_tikla(driver, btn)
                            giris_tiklandi = True
                            self.log_yaz("Giriş butonuna tıklandı.")
                            break
                    if giris_tiklandi: break
                except: continue
            
            if not giris_tiklandi:
                self.log_yaz("⚠ Standart buton bulunamadı, JS ile zorlanıyor...")
                try:
                    driver.execute_script("""
                        var btns = document.querySelectorAll('button, a');
                        for (var i=0; i<btns.length; i++) {
                            if (btns[i].innerText.includes('GİRİŞ') || btns[i].innerText.includes('Giriş')) {
                                btns[i].click();
                                break;
                            }
                        }
                    """)
                    time.sleep(1)
                except: pass

            self.log_yaz("Bilgiler giriliyor (İnsan gibi yazılıyor)...")

            try:
                u_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@name='username' or @type='text']")))
                self.human_type(u_box, data["user"])
                
                p_box = driver.find_element(By.XPATH, "//input[@type='password']")
                self.human_type(p_box, data["pass"])
                p_box.send_keys(Keys.ENTER)
                
                try: driver.find_element(By.XPATH, "//button[@type='submit']").click()
                except: pass
            except: 
                self.log_yaz("⚠ Giriş kutuları açılamadı.")
                if driver: driver.quit()
                return

            self.log_yaz("2FA bekleniyor...")
            time.sleep(5) 
            
            try:
                opt_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'E-posta') or contains(text(), 'E-mail')]")
                if opt_elem.is_displayed(): self.js_tikla(driver, opt_elem); time.sleep(1)
                
                snd = driver.find_element(By.XPATH, "//*[contains(text(), 'GÖNDER') or contains(text(), 'Devam')]")
                if snd.is_displayed(): 
                    self.js_tikla(driver, snd)
                    self.log_yaz("İlk Kod istendi.")
            except: pass

            basari = False
            for deneme in range(1, 4):
                self.log_yaz(f"Tur {deneme}/3: Kod aranıyor...")
                self.captcha_kontrol(driver)
                
                self.log_yaz("Mail bekleniyor (15sn)...")
                time.sleep(15) 

                kod = None
                t_start = time.time()
                while time.time() - t_start < 40: 
                    kod = self.kod_cek(data["gmail"], data["gmail_pass"])
                    if kod: break
                    time.sleep(3)
                
                if kod:
                    self.log_yaz(f"KOD BULUNDU: {kod}")
                    try:
                        kod_kutulari = driver.find_elements(By.TAG_NAME, "input")
                        hedef_kutu = None
                        for k in kod_kutulari:
                            if k.is_displayed() and k.get_attribute("type") in ["text", "number", "tel"]: hedef_kutu = k; break
                        
                        if hedef_kutu:
                            driver.execute_script("arguments[0].click();", hedef_kutu)
                            hedef_kutu.send_keys(Keys.CONTROL + "a"); hedef_kutu.send_keys(Keys.DELETE); time.sleep(0.5)
                            for rakam in str(kod): hedef_kutu.send_keys(rakam); time.sleep(0.15)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", hedef_kutu)
                            hedef_kutu.send_keys(Keys.TAB)
                            time.sleep(2)
                            try: hedef_kutu.send_keys(Keys.ENTER)
                            except: pass
                            onayla = None
                            xpath_list = ["//*[contains(text(), 'ONAY') or contains(text(), 'Onay')]", "//*[contains(text(), 'DOĞRULA') or contains(text(), 'Doğrula')]", "//button[@type='submit']"]
                            for xp in xpath_list:
                                try:
                                    found = driver.find_elements(By.XPATH, xp)
                                    for f in found:
                                        if f.is_displayed(): onayla = f; break
                                    if onayla: break
                                except: continue
                            
                            if onayla:
                                driver.execute_script("arguments[0].click();", onayla)
                                self.log_yaz("🖱 Butona tıklandı. Kontrol ediliyor...")
                                time.sleep(3)
                                
                                try:
                                    if hedef_kutu.is_displayed():
                                        self.log_yaz("Kod kabul edilmedi/Yanlış kod.")
                                    else:
                                        self.log_yaz("GİRİŞ BAŞARILI!")
                                        winsound.Beep(1000, 200); basari = True; break
                                except:
                                    self.log_yaz("GİRİŞ BAŞARILI!")
                                    winsound.Beep(1000, 200); basari = True; break
                            
                        else: self.log_yaz("Kod kutusu yok.")
                    except: pass
                else: self.log_yaz("Kod gelmedi.")
                
                if basari: break
                
                self.log_yaz("Kod işe yaramadı, 'Yeniden Gönder'e basılıyor...")
                try:
                    resend = driver.find_element(By.XPATH, "//*[contains(text(), 'YENİDEN') or contains(text(), 'Tekrar')]")
                    self.js_tikla(driver, resend)
                    time.sleep(5)
                except: 
                    self.log_yaz("⚠ Yeniden gönder butonu bulunamadı.")

            if not basari: self.log_yaz("Giriş yapılamadı.")

        except Exception as e:
            self.log_yaz(f"Kritik Hata: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass

if __name__ == "__main__":
    app = BotApp()
    app.mainloop()
