from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import random

app = Flask(__name__)

# --- WhatsApp API Credentials ---
VERIFY_TOKEN = "litewaybot"  # your verify token
ACCESS_TOKEN = "EAAV8xZCoaLukBPqIg6XNacZA7nsjaBX2arJ1votPolGPtKBvP6unirusvvRxYFTyLvDKdJ5AlEYAjNSrz58H34JS2MZA0ReLim0ZACVlxUKQyPZAIML5vQqnWARced0BYdeqWXjzMrvQkFZBmSYilsGz6ZA66Jx3NbZAUlUKu3EUrKDyxpj0wYa57hbZCnEGZCvrZAETZA2cCP7Mc2UdbZBW46NQxcoZAmUZCkMsDVriCZCJHXhQL5kZD"
PHONE_NUMBER_ID = "823077057555789"  # your WhatsApp phone number ID


# --- Home route ---
@app.route('/', methods=['GET'])
def home():
    return "WhatsApp VTU Bot is live!", 200


# --- Webhook Verification (GET request) ---
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        return "Verification failed", 403


# --- Webhook for incoming messages (POST request) ---
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Incoming data:", data)

    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            name = data["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

            # --- If message is interactive (button reply) ---
            if message.get("type") == "interactive":
                button_reply = message["interactive"]["button_reply"]["id"]

                if button_reply == "buy_data":
                    link = f"https://whatsapp-bot-kivv.onrender.com/data?user={sender}"
                    send_message(sender, f"📶 Click below to continue buying data:\n{link}")

                elif button_reply == "buy_airtime":
                    send_message(sender, "💡 Airtime purchase coming soon!")

                elif button_reply == "pay_bills":
                    send_message(sender, "🧾 Bill payment feature coming soon!")

            # --- If message is a text ---
            elif message.get("type") == "text":
                text = message["text"]["body"].strip().lower()
                if text in ["hi", "hello", "hey"]:
                    reply_with_buttons(sender, name)
                else:
                    send_message(sender, f"You said: {text}")

    except Exception as e:
        print("Error:", e)

    return jsonify(success=True), 200


# --- Function: Send text message ---
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


# --- Function: Reply with buttons (main menu) ---
def reply_with_buttons(to, name):
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
            "body": {
                "text": f"Hello {name}! 👋\nWhat would you like to do today?"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "buy_data", "title": "Buy Data"}},
                    {"type": "reply", "reply": {"id": "buy_airtime", "title": "Buy Airtime"}},
                    {"type": "reply", "reply": {"id": "pay_bills", "title": "Pay Bills"}}
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Response:", response.text)


# --- Web page: Data purchase form ---
@app.route('/data', methods=['GET'])
def data_form():
    user = request.args.get("user", "")
    return f"""
    <html>
      <head><title>Buy Data</title></head>
      <body style='font-family: Arial; padding: 20px'>
        <h2>Buy Data</h2>
        <form action="/process_data" method="post">
          <input type="hidden" name="user" value="{user}">
          <label>Network:</label><br>
          <select name="network" required>
            <option>MTN</option>
            <option>GLO</option>
            <option>AIRTEL</option>
            <option>9MOBILE</option>
          </select><br><br>

          <label>Data Plan:</label><br>
          <select name="plan" required>
            <option value="500">1GB - ₦500</option>
            <option value="1000">2GB - ₦1000</option>
            <option value="1500">3GB - ₦1500</option>
          </select><br><br>

          <label>Phone Number:</label><br>
          <input type="text" name="phone" placeholder="e.g. 08123456789" required><br><br>

          <button type="submit">Continue</button>
        </form>
      </body>
    </html>
    """


# --- Process the form submission ---
@app.route('/process_data', methods=['POST'])
def process_data():
    user = request.form.get("user")
    network = request.form.get("network")
    plan = request.form.get("plan")
    phone = request.form.get("phone")

    # Generate transaction ref
    ref = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
    amount = plan

    # Temporary virtual account (mock)
    virtual_account = "1234567890"
    bank_name = "Moniepoint Bank"

    # Send confirmation to WhatsApp
    message = (
        f"📶 *Data Purchase Summary:*\n\n"
        f"Network: {network}\n"
        f"Phone: {phone}\n"
        f"Amount: ₦{amount}\n"
        f"Ref: {ref}\n\n"
        f"💳 Please pay ₦{amount} to:\n"
        f"*{virtual_account} ({bank_name})*\n\n"
        f"Once payment is confirmed, data will be sent automatically ✅"
    )
    send_message(user, message)

    return "<h3>Transaction initiated! Check your WhatsApp for payment details.</h3>"


# --- Run Flask App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
