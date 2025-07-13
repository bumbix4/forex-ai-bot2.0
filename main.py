import os
import openai
import requests

openai.api_key = os.environ["OPENAI_API_KEY"]
telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

def get_analysis():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional Forex analyst."},
            {"role": "user", "content": """
Act as a world-class Forex analyst. Provide an intraday analysis for XAU/USD.
Use current technical indicators (assume RSI ~68, price ~2370, bullish pressure).
Respond with: trend, key levels, setup idea (entry, SL, TP), and confidence level.
"""}
        ]
    )
    return response["choices"][0]["message"]["content"]

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    try:
        analysis = get_analysis()
        print("✅ ANALYSIS GENERATED:\n", analysis)
        send_to_telegram(analysis)
        print("✅ MESSAGE SENT TO TELEGRAM")
    except Exception as e:
        print("❌ ERROR:", e)
