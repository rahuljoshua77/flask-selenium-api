from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
app = Flask(__name__)

class BrowserSession:
    def __init__(self):
        self.browser = None

    def get_browser(self):
        if not self.browser:
            self.init_browser()
        return self.browser

    def init_browser(self):
        opts = Options()
        opts.add_argument('--disable-setuid-sandbox')
        opts.add_argument('disable-infobars')
        opts.add_argument('--headless=chrome')
        opts.add_argument('--no-first-run')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument("--disable-infobars")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-popup-blocking")
        opts.add_argument('--log-level=3') 
        # opts.add_argument("--start-maximized")
        # opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_argument('--disable-notifications')
        mobile_emulation = {
            "deviceMetrics": {"width": 350, "height": 880, "pixelRatio": 5.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
        }
        #opts.add_argument('--headless=new')
        opts.add_argument("window-size=200,100")
        opts.add_experimental_option("mobileEmulation", mobile_emulation)
        opts.add_argument(f"user-agent=Mozilla/5.0 (Linux; Android 9.0; SAMSUNG SM-F900U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")

        self.browser = webdriver.Chrome(ChromeDriverManager().install(), options=opts)

    def close_browser(self):
        if self.browser:
            self.browser.quit()
            self.browser = None

def open_browser(data):
    browser_session = BrowserSession()
    browser = browser_session.get_browser()
     
    for i in range(0, 10):
        try:
            browser.get('https://cekdptonline.kpu.go.id/')

            wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//input[contains(@class,"form-control")]'))).send_keys(data)
            wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//input[contains(@class,"form-control")]'))).send_keys(Keys.ENTER)

            check = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(),"Kecamatan") or contains(text(),"belum terdaftar!")]'))).text

            if "Kecamatan" in str(check) or "kecamatan" in str(check) or "Kecamatan" == check:
                kabupaten = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//p[@class="row--left"]/span[contains(text(),"Kabupaten")]/parent::p'))).text
                kabupaten = kabupaten.replace('Kabupaten', '')
                kecamatan = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[3]/div[3]/div[3]/div[1]/p[2]'))).text
                kecamatan = kecamatan.replace('Kecamatan', '').strip()
                kelurahan = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[3]/div/div[3]'))).text
                no = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '(//div[@class="top--side"]//div)[3]'))).text
                tps = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '(//div[@class="top--side"]//div)[4]'))).text
                nama = wait(browser, 15).until(EC.presence_of_element_located((By.XPATH, '//span[text()="Nama Pemilih"]/parent::p'))).text
                nama = nama.replace('Nama Pemilih', '').strip()

                result = {
                    'nik': data,
                    'nama': nama,
                    'no': no.strip(),
                    'tps': tps.strip(),
                    'kecamatan': kecamatan.strip(),
                    'kelurahan': kelurahan.strip(),
                    'kabupaten': kabupaten.strip()
                }

                # Process the result or return it as needed
                browser_session.close_browser()

                return result
            else:
                # If data is not found, continue to the next iteration
                continue
        except Exception as e:
            return {'nik': data, 'message': f"Error: {e} or API is used, please wait for the other request to finish!"}

    # Move the browser closing outside the loop
    browser_session.close_browser()

    # If the loop completes without finding the data, return a message indicating that the data was not found
    return {'nik': data, 'message': 'Data not found!'}

def process_request(data):
    try:
        result = open_browser(data)
        return {'message': 'API call successful', 'result': result}
    except Exception as e:
        return {'error': str(e)}

@app.route('/api/cekdpt', methods=['POST'])
def call_cekdptonline_concurrent():
    inp_data = request.json.get('data')

    if not inp_data:
        return jsonify({'error': 'data is required'}), 400

    # Use ThreadPoolExecutor to execute the function asynchronously
    with ThreadPoolExecutor() as executor:
        result = executor.submit(process_request, inp_data).result()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=11111)
