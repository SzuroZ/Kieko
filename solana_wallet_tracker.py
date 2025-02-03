import asyncio
import sys
import os
from flask import Flask, jsonify, render_template
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import threading
from datetime import datetime, timedelta
import pytz  # For time zone handling

# Segédfüggvény az EXE fájlban való fájl elérési utak kezelésére
def get_resource_path(relative_path):
    """Adja vissza a fájl elérési útját, függetlenül attól, hogy EXE vagy fejlesztési környezetben fut-e."""
    try:
        # Ha az alkalmazás EXE-ben fut, a PyInstaller elérési útját kell használni
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# A statikus fájlok elérési útja
static_folder = get_resource_path("static")
templates_folder = get_resource_path("templates")

app = Flask(__name__, static_folder=static_folder, template_folder=templates_folder)

WALLET_ADDRESS = "3RmzSs3B1Qd6Kf3LTN6r3W5TQhh7M6hBnntpEExMr17m"
wallet_data = {"balance": 0, "pnl": 0}
reference_balance = None  # Inicializálás dinamikusan


async def get_balance(wallet_address: str, retries=5) -> int:
    """Lekéri a tárca egyenlegét, és ha hiba történik, újrapróbálja."""
    wallet = Pubkey.from_string(wallet_address)
    
    for attempt in range(retries):
        try:
            async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
                response = await client.get_balance(wallet)
                return response.value
        except Exception as e:
            print(f"Balance fetch error (attempt {attempt+1}/{retries}): {e}")
            await asyncio.sleep(2)  # Várunk 2 másodpercet újrapróbálkozás előtt

    print("Final error: Unable to fetch balance after multiple attempts.")
    return None  # Jelzés, hogy nem sikerült lekérni


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
            continue  # Újrapróbálkozás

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
