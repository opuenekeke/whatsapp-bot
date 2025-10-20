from flask import Flask, request, jsonify, render_template
import requests
import os
import random
import string

app = Flask(__name__)

# --- WhatsApp API Credentials ---
VERIFY_TOKEN = "litewaybot"
ACCESS_TOKEN = "EAAV8xZCoaLukBPkHZAUzpnTK8R1h4LyZAOToixMy0mS2ojsaRAGMX0LTF3CLpIKjrYZCQ0I38d3mtPWVtIvUzhc1RRJGIkuI1qWaaZC6OIA7pFWFIHT1qxYAMbk7mNgfC8a4RTU3tYpwZAoKmWwlRGFy60HE912H9iI35OgNd1yzo99R3NSKzm3XSPHOlKT6FBHOU2mvZCTL6IUsESW2GgNVV5WZCQ0C4ALmzVSrIgdAbAZDZD"
PHONE_NUMBER_ID = "823077057555789"


@app.route('/', methods=['GET'])
def home():
    return "✅ WhatsApp VTU Bot is running!", 200


# --- Webhook Verification ---
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    return "Verification failed", 403


# --- Handle Incoming Messages ---
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Incoming data:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            message = value["messages"][0]
            sender = message["from"]
            user_name = value["contacts"][0]["profile"]["name"]
            text = message.get("text", {}).get("body", "").lower().strip()

            # GREETING
            if text in ["hi", "hello", "hey"]:
                reply = (
                    f"Hello {user_name}! 👋\n"
                    f"What would you like to do today?\n\n"
                    f"✅ Buy Data\n"
                    f"💳 Buy Airtime\n"
                    f"🧾 Pay Bills"
                )
                send_message(sender, reply)

            # BUY DATA
            elif "data" in text or text == "1":
                send_button_message(sender)

            # BUY AIRTIME
            elif "airtime" in text or text == "2":
                send_message(sender, "💳 Airtime purchase feature is coming soon!")

            # PAY BILLS
            elif "bill" in text or text == "3":
                send_message(sender, "🧾 Bill payment service will be live shortly!")

            else:
                send_message(sender, "❓ I didn’t understand that. Please type *Hi* to start again.")

    except Exception as e:
        print("Error:", e)

    return jsonify(success=True), 200


# --- SEND TEXT MESSAGE ---
def send_message(to, message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Response:", response.text)


# --- SEND BUTTON MESSAGE (Clickable Link) ---
def send_button_message(to):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "📱 Great! Tap below to continue your Data Purchase:"},
            "action": {
                "buttons": [
                    {
                        "type": "url",
                        "url": "https://whatsapp-bot-kivv.onrender.com/data-form",
                        "title": "🟢 Open Data Form"
                    }
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Response:", response.text)


# --- HTML FORM PAGE ---
@app.route('/data-form', methods=['GET'])
def data_form():
    return render_template("data_form.html")


# --- PROCESS DATA FORM ---
@app.route('/process-data', methods=['POST'])
def process_data():
    network = request.form.get("network")
    plan = request.form.get("plan")
    phone = request.form.get("phone")

    # Generate fake reference and virtual account
    ref = "TXN" + ''.join(random.choices(string.digits, k=8))
    vaccount = "901" + ''.join(random.choices(string.digits, k=7))

    return render_template(
        "payment_summary.html",
        network=network,
        plan=plan,
        phone=phone,
        ref=ref,
        vaccount=vaccount
    )


# --- RUN APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)










<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Buy Data</title>
  <style>
    body {
      font-family: "Segoe UI", sans-serif;
      background: #f2f5f7;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .form-container {
      background: #fff;
      padding: 25px 30px;
      border-radius: 15px;
      box-shadow: 0 3px 10px rgba(0,0,0,0.1);
      width: 90%;
      max-width: 400px;
    }
    h2 {
      text-align: center;
      color: #007b5e;
    }
    label {
      display: block;
      margin-top: 10px;
      font-weight: 600;
    }
    select, input {
      width: 100%;
      padding: 8px;
      margin-top: 5px;
      border-radius: 6px;
      border: 1px solid #ccc;
    }
    button {
      width: 100%;
      margin-top: 20px;
      background: #007b5e;
      color: white;
      border: none;
      padding: 10px;
      font-size: 16px;
      border-radius: 6px;
      cursor: pointer;
    }
    button:hover {
      background: #005f47;
    }
  </style>
</head>
<body>
  <div class="form-container">
    <h2>Buy Data</h2>
    <form action="/process-data" method="POST">
      <label>Network</label>
      <select name="network" required>
        <option value="">Select Network</option>
        <option value="MTN">MTN</option>
        <option value="GLO">GLO</option>
        <option value="Airtel">Airtel</option>
        <option value="9mobile">9mobile</option>
      </select>

      <label>Data Plan</label>
      <select name="plan" required>
        <option value="">Select Plan</option>
        <option value="500MB - ₦200">500MB - ₦200</option>
        <option value="1GB - ₦350">1GB - ₦350</option>
        <option value="2GB - ₦700">2GB - ₦700</option>
      </select>

      <label>Phone Number</label>
      <input type="tel" name="phone" placeholder="e.g. 08012345678" required>

      <button type="submit">Continue</button>
    </form>
  </div>
</body>
</html>
