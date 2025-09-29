import json
import requests
import hmac
import hashlib
import datetime
import threading
import tracemalloc

# Discord & Telegram
import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# =================== AMAZON PA-API CREDENTIALS ===================
ACCESS_KEY = "AKPAIL6D0C1759150638"
SECRET_KEY = "JBpb9z2EKnzIOEJb/KaAgHFIBXetTid++rNBGJdx"
PARTNER_TAG = "carlindsouza-21"
REGION = "us-east-1"
HOST = "webservices.amazon.in"
ENDPOINT = "https://webservices.amazon.in/paapi5/searchitems"

# =================== TELEGRAM & DISCORD TOKENS ===================
TELEGRAM_TOKEN = "8026700335:AAGYCtaNThVTbVkEbXEKpKixj9P60vKnNOw"
DISCORD_TOKEN = "MTQyMjI1MTkzOTY5NzAwNDcwNw.Gcq-UL.giYb9gm6hs2xCTIHBdOp4CuIYP3_vr6Xv0segc"

# =================== HELPER FUNCTIONS ===================
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region, service):
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing

def fetch_amazon_results(keywords, max_results=3):
    method = 'POST'
    service = 'ProductAdvertisingAPI'
    content_type = 'application/json; charset=UTF-8'

    request_parameters = {
        "Keywords": keywords,
        "PartnerTag": PARTNER_TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.in",
        "Resources": ["ItemInfo.Title", "Offers.Listings.Price"]
    }

    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    canonical_uri = '/paapi5/searchitems'
    canonical_querystring = ''
    payload = json.dumps(request_parameters)
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    canonical_headers = f'content-encoding:utf-8\nhost:{HOST}\nx-amz-date:{amzdate}\nx-amz-target:com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems\n'
    signed_headers = 'content-encoding;host;x-amz-date;x-amz-target'
    canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f"{datestamp}/{REGION}/{service}/aws4_request"
    string_to_sign = f"{algorithm}\n{amzdate}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    signing_key = get_signature_key(SECRET_KEY, datestamp, REGION, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization_header = f"{algorithm} Credential={ACCESS_KEY}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

    headers = {
        'Content-Encoding': 'utf-8',
        'Content-Type': content_type,
        'Host': HOST,
        'X-Amz-Date': amzdate,
        'X-Amz-Target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems',
        'Authorization': authorization_header
    }

    try:
        response = requests.post(ENDPOINT, data=payload, headers=headers)
        data = response.json()
        results = []
        for item in data.get("SearchResult", {}).get("Items", [])[:max_results]:
            title = item["ItemInfo"]["Title"]["DisplayValue"]
            url = item["DetailPageURL"]
            results.append({"title": title, "url": url})
        return results
    except Exception as e:
        print("Amazon API Error:", e)
        return []

# =================== TELEGRAM BOT ===================
async def search_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("⚡ Usage: /search <product>")
        return
    results = fetch_amazon_results(query)
    if results:
        reply = "\n\n".join([f"🔹 {r['title']}\n{r['url']}" for r in results])
    else:
        reply = "No results found."
    await update.message.reply_text(reply)

def run_telegram():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("search", search_telegram))
    app.run_polling()

# =================== DISCORD BOT ===================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def amazon(ctx, *, query):
    results = fetch_amazon_results(query)
    if results:
        reply = "\n\n".join([f"**{r['title']}**\n{r['url']}" for r in results])
    else:
        reply = "No results found."
    await ctx.send(reply)

def run_discord():
    bot.run(DISCORD_TOKEN)

# =================== MAIN ===================
if __name__ == "__main__":
    threading.Thread(target=run_telegram()).start()
    threading.Thread(target=run_discord()).start()
  
