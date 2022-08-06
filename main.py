import requests
from twilio.rest import Client
from decouple import config

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = config("STOCK_API_KEY")
NEWS_API_KEY = config("NEWS_API_KEY")

TWILIO_NUMBER = config("TWILIO_PHONE")
PERSONAL_NUMBER = config("PERSONAL_PHONE")

acc_sid = config("ACC_SID")
auth_token = config("AUTH_TOKEN")

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY
}

news_params = {
    "apiKey": NEWS_API_KEY,
    "qInTitle": COMPANY_NAME
}

client = Client(acc_sid, auth_token)

r1 = requests.get(STOCK_ENDPOINT, params=stock_params)
data = r1.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]

yesterday = float(data_list[0]["4. close"])
before_yesterday = float(data_list[1]["4. close"])

positive_diff = round(abs(yesterday - before_yesterday), 2)
percentage = int(round((positive_diff/yesterday) * 100, 0))

if yesterday > before_yesterday:
    stock_report = f"{STOCK_NAME}: 🔺{percentage}%"
else:
    stock_report = f"{STOCK_NAME}: 🔻{percentage}%"

if percentage > 5:
    r2 = requests.get(NEWS_ENDPOINT, params=news_params)
    news_data = r2.json()["articles"]
    articles = news_data[:3]
    
    formatted_articles = [f"{stock_report} \nHeadline: {article['title']}. \nBrief: {article['description']}" for article in articles]
    
    for article in formatted_articles:
        message = client.messages \
                    .create(
                        body=f"{article}",
                        from_=TWILIO_NUMBER,
                        to=PERSONAL_NUMBER
                    )
        print(message.status)
else:
    message = client.messages \
                    .create(
                        body=f"{stock_report} \nNo news for you!",
                        from_=TWILIO_NUMBER,
                        to=PERSONAL_NUMBER
                    )
    print(message.status)

