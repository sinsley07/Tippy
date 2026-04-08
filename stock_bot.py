import requests
from bs4 import BeautifulSoup
import time
import os
import re

# 從環境變數讀取 (GitHub Secrets 會自動注入)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STOCK_SYMBOL = os.environ.get("STOCK_SYMBOL", "2330")

def get_stock_price():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    url = f"https://tw.stock.yahoo.com/quote/{STOCK_SYMBOL}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # 尋找股價數字的邏輯 (與您測試成功的版本相同)
        for span in soup.find_all(['span', 'div']):
            text = span.text.strip()
            if re.match(r'^[\d,]+(\.\d+)?$', text):
                if len(text) <= 15:
                    clean_price = text.replace(',', '')
                    try:
                        if 10 < float(clean_price) < 2000:
                            return text
                    except:
                        pass
        return None
    except Exception as e:
        print(f"錯誤: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("錯誤：請設定環境變數")
        return
    price = get_stock_price()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    if price:
        message = f"📈 <b>{STOCK_SYMBOL} 即時股價</b>\n🕒 {current_time}\n💰 價格：{price} 元"
    else:
        message = f"⚠️ 無法取得 {STOCK_SYMBOL} 股價\n🕒 {current_time}"
    send_telegram(message)

if __name__ == "__main__":
    main()
