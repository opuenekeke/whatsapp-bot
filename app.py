from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# --- WhatsApp API Credentials ---
VERIFY_TOKEN = "litewaybot"  # same verify token used on Facebook
ACCESS_TOKEN = "EAAV8xZCoaLukBPqIg6XNacZA7nsjaBX2arJ1votPolGPtKBvP6unirusvvRxYFTyLvDKdJ5AlEYAjNSrz58H34JS2MZA0ReLim0ZACVlxUKQyPZAIML5vQqnWARced0BYdeqWXjzMrvQkFZBmSYilsGz6ZA66Jx3NbZAUlUKu3EUrKDyxpj0wYa57hbZCnEGZCvrZAETZA2cCP7Mc2UdbZBW46NQxcoZAmUZCkMsDVriCZCJHXhQL5kZD"

PHONE_NUMBER_ID = "823077057555789"  # your WhatsApp phone number ID


@app.route('/', methods=['GET'])
def home():
    return "WhatsApp Bot is live!", 200


# --- Webhook verification (GET request) ---
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


# --- Handle incoming messages (POST request) ---
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Incoming data:", data)

    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            text = message.get("text", {}).get("body", "").strip().lower()

            # Get user's WhatsApp name
            contact_info = data["entry"][0]["changes"][0]["value"].get("contacts", [])
            name = contact_info[0]["profile"]["name"] if contact_info else "there"

            # --- Reply with interactive buttons ---
            if text in ["hi", "hello", "hey"]:
                reply_with_buttons(sender, name)
            else:
                reply_text = f"You said: {text}"
                send_message(sender, reply_text)

    except Exception as e:
        print("Error:", e)

    return jsonify(success=True), 200


# --- Function to send normal text messages ---
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
    print("Text Response:", response.text)


# --- Function to send interactive buttons ---
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
                "text": f"👋 Hello *{name}!* \nWhat would you like to do today?"
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
    print("Button Response:", response.text)


# --- Run the Flask app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
