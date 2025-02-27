import asyncio
import sys
import os
import subprocess
from flask import Flask, jsonify, render_template
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import threading
from datetime import datetime, timedelta
import pytz  # For time zone handling

# Helper function to handle file paths for EXE files
def get_resource_path(relative_path):
    """Returns the file path, regardless of whether the app is running in an EXE or development environment."""
    try:
        # If the app is running in an EXE, use the PyInstaller path
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Indítsd el az Ngrokot egy külön folyamatban
def start_ngrok():
    ngrok_command = "ngrok http 5000"
    subprocess.Popen(ngrok_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# Set the paths for static files and templates
static_folder = get_resource_path("static")
templates_folder = get_resource_path("templates")

app = Flask(__name__, static_folder=static_folder, template_folder=templates_folder)

WALLET_ADDRESS = "8T7rZ1AtF8hSm2gTu2JYqPRGeujdp2P8YsCk7sADhPjV"
wallet_data = {"balance": 0, "pnl": 0}
reference_balance = None  # Initialize dynamically

async def get_balance(wallet_address: str, retries=5) -> int:
    """Fetches the wallet balance and retries if an error occurs."""
    wallet = Pubkey.from_string(wallet_address)
    
    for attempt in range(retries):
        try:
            async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
                response = await client.get_balance(wallet)
                return response.value
        except Exception as e:
            print(f"Balance fetch error (attempt {attempt+1}/{retries}): {e}")
            await asyncio.sleep(2)  # Wait for 2 seconds before retrying

    print("Final error: Unable to fetch balance after multiple attempts.")
    return None  # Indicate that the balance could not be fetched

async def track_balance():
    global wallet_data, reference_balance

    initial_balance = await get_balance(WALLET_ADDRESS)
    if initial_balance is None:
        print("Error: Unable to fetch initial balance")
        return

    reference_balance = initial_balance / 1_000_000_000
    wallet_data["balance"] = reference_balance
    wallet_data["pnl"] = 0

    while True:
        current_balance = await get_balance(WALLET_ADDRESS)
        
        if current_balance is None:
            print("Error: Failed to fetch balance. Retrying...")
            wallet_data["balance"] = "Error fetching balance"
            wallet_data["pnl"] = "Error fetching balance"
            await asyncio.sleep(3)
            continue  # Retry

        wallet_data["balance"] = current_balance / 1_000_000_000
        wallet_data["pnl"] = wallet_data["balance"] - reference_balance
        await asyncio.sleep(3)

async def reset_pnl_at_11_59pm():
    global reference_balance, wallet_data

    while True:
        est = pytz.timezone("US/Eastern")
        now = datetime.now(est)

        next_11_59pm = now.replace(hour=23, minute=59, second=0, microsecond=0)
        if now >= next_11_59pm:
            next_11_59pm += timedelta(days=1)

        time_until_reset = (next_11_59pm - now).total_seconds()
        print(f"Time until next reset: {time_until_reset} seconds")
        await asyncio.sleep(time_until_reset)

        current_balance = await get_balance(WALLET_ADDRESS)
        if current_balance is not None:
            reference_balance = current_balance / 1_000_000_000
            wallet_data["pnl"] = 0
            print("PNL reset at 11:59 PM EST")
        else:
            print("Error during PNL reset: Failed to fetch balance")

@app.route("/balance")
def balance():
    return jsonify(wallet_data)

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Exception on {request.path} [GET]", exc_info=e)
    return "An error occurred", 500

@app.route("/")
def index():
    return render_template("index.html")

def start_server():
    app.run(host="0.0.0.0", port=5000)

def start_async_loop():
    asyncio.run(main())

async def main():
    await asyncio.gather(track_balance(), reset_pnl_at_11_59pm())

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    start_async_loop()