from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# --- WhatsApp API Credentials ---
VERIFY_TOKEN = "litewaybot"
ACCESS_TOKEN = "EAAV8xZCoaLukBPqIg6XNacZA7nsjaBX2arJ1votPolGPtKBvP6unirusvvRxYFTyLvDKdJ5AlEYAjNSrz58H34JS2MZA0ReLim0ZACVlxUKQyPZAIML5vQqnWARced0BYdeqWXjzMrvQkFZBmSYilsGz6ZA66Jx3NbZAUlUKu3EUrKDyxpj0wYa57hbZCnEGZCvrZAETZA2cCP7Mc2UdbZBW46NQxcoZAmUZCkMsDVriCZCJHXhQL5kZD"

PHONE_NUMBER_ID = "823077057555789"

@app.route('/', methods=['GET'])
def home():
    return "WhatsApp VTU Bot is running!", 200


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
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            user_name = data["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
            text = message.get("text", {}).get("body", "").lower().strip()

            if text in ["hi", "hello", "hey"]:
                reply = f"Hello {user_name}! 👋\nWhat would you like to do today?\n\n1️⃣ Buy Data\n2️⃣ Buy Airtime\n3️⃣ Pay Bills"
                send_message(sender, reply)

            elif text in ["1", "buy data"]:
                reply = (
                    f"📱 Great! To buy data, please fill this quick form:\n\n"
                    f"*Click below to continue 👇*\n"
                    f"[🟢 Open Data Form](https://whatsapp-bot-kivv.onrender.com/data-form)"
                )
                send_message(sender, reply)

            elif text in ["2", "buy airtime"]:
                send_message(sender, "💳 Airtime purchase feature is coming soon!")

            elif text in ["3", "pay bills"]:
                send_message(sender, "🧾 Bill payment service will be live shortly!")

            else:
                send_message(sender, "❓ I didn’t understand that. Please reply with 1, 2, or 3.")

    except Exception as e:
        print("Error:", e)

    return jsonify(success=True), 200


# --- Function to Send WhatsApp Message ---
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


# --- HTML Form for Buying Data ---
@app.route('/data-form', methods=['GET'])
def data_form():
    return render_template("data_form.html")


# --- Run Flask App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
