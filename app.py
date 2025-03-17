import socket
import requests
from flask import Flask, render_template, request, jsonify
    
app = Flask(__name__)

# Telegram Bot Details
TELEGRAM_BOT_TOKEN = "7482322952:AAGQtIZCnJ-Yp0UBsCEp0F0IdhA8FGwKaBc"
TELEGRAM_CHAT_ID = "1480524595"

# ESP32 Communication (Simulated)
def send_to_esp32(message):
    # PORT = 8080
    # ESP32_IP = "192.168.142.240"  # Change this to your ESP32's IP
    print(f"Sending to ESP32: {message}")
    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect((ESP32_IP, PORT))
    # client.sendall((message + "\n").encode())  # Send message with newline
    # client.close()
    print("DONE")

# Telegram Bot Function
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/table/<int:table_number>")
def table(table_number):
    send_to_esp32(f"C-{table_number:02d}")
    return render_template("menu.html", table_number=table_number)

@app.route("/confirm_order", methods=["POST"])
def confirm_order():
    data = request.json
    table_number = data["table_number"]
    items = data["items"]
    total_amount = float(data["total_amount"])  # Convert total_amount to float
    total_amount_with_gst = total_amount + (total_amount * 0.12)  # Add 12% GST
    total_items = sum(item["quantity"] for item in items)  # Calculate total items

    # Print order details
    print(f"\n📌 Order Confirmed for Table {table_number}:")
    for item in items:
        print(f"➡️ {item['name']} - {item['quantity']} x ₹{item['price']}")
    print(f"💰 Total Amount (with GST): ₹{total_amount_with_gst}, 🛒 Total Items: {total_items}\n")

    # Send confirmation to Telegram
    message = f"✅ Order confirmed for Table {table_number}:\n"
    for item in items:
        message += f"🍽 {item['name']} - {item['quantity']} x ₹{item['price']}\n"
    message += f"\n💵 Total Amount (with GST): ₹{total_amount_with_gst}, 🛒 Total Items: {total_items}"
    
    send_to_telegram(message)
    
    return jsonify({
        "status": "success",
        "redirect_url": f"/order_confirmed?total_items={total_items}&total_amount={total_amount_with_gst}"
    })

@app.route("/order_confirmed")
def order_confirmed():
    total_items = request.args.get("total_items", 0)
    total_amount = request.args.get("total_amount", 0)
    return render_template("order_confirmed.html", total_items=total_items, total_amount=total_amount)

if __name__ == "__main__":
    app.run(debug=True)