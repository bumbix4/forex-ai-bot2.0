import os
import openai
import requests
import time

# CONFIG
openai.api_key = os.environ["OPENAI_API_KEY"]
telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]
alpha_key = os.environ["ALPHA_VANTAGE_KEY"]

pairs = {
    "XAU/USD": "XAUUSD",
    "EUR/USD": "EURUSD",
    "GBP/JPY": "GBPJPY",
    "USD/CHF": "USDCHF"
}

def get_rsi(pair):
    url = f"https://www.alphavantage.co/query?function=RSI&symbol={pair}&interval=15min&time_period=14&series_type=close&apikey={alpha_key}"
    response = requests.get(url).json()
    try:
        rsi = list(response["Technical Analysis: RSI"].values())[0]["RSI"]
        return float(rsi)
    except:
        return "N/A"

def get_price(pair):
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={pair[:3]}&to_currency={pair[-3:]}&apikey={alpha_key}"
    response = requests.get(url).json()
    try:
        price = response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        return float(price)
    except:
        return "N/A"

def build_prompt(data):
    prompt = "You are a world-class Forex analyst. Generate a brief, tactical intraday analysis for the following currency pairs based on RSI and price:\n\n"
    for pair, info in data.items():
        prompt += f"{pair}: Price = {info['price']}, RSI = {info['rsi']}\n"
    prompt += "\nFor each pair, output: trend, entry idea, SL, TP, and confidence level. Be concise."
    return prompt

def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional Forex strategist."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def main():
    data = {}
    for name, symbol in pairs.items():
        rsi = get_rsi(symbol)
        price = get_price(symbol)
        data[name] = {"rsi": rsi, "price": price}
        time.sleep(15)  # respectă limita Alpha Vantage (5 calls/min)

    prompt = build_prompt(data)
    print("📩 Prompt GPT:\n", prompt)
    analysis = ask_gpt(prompt)
    print("✅ GPT Response:\n", analysis)
    send_telegram(analysis)

if __name__ == "__main__":
    main()
