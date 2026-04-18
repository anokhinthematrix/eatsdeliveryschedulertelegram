import logging
import os
import time
from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.background import BackgroundScheduler

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ADMIN_IDS = [804349433]

BOLT_THREAD_ID = 10
GLOVO_THREAD_ID = 12
WOLT_THREAD_ID = 6

TIMEZONE = "Europe/Bucharest"
POLL_INTERVAL_SECONDS = 2
REQUEST_TIMEOUT = 15

TEST_MODE = True

last_update_id = None

if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN environment variable")

if not CHAT_ID:
    raise ValueError("Missing CHAT_ID environment variable")

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =========================
# MESSAGES
# =========================

BOLT_MESSAGE_1 = """

🔄 <b>În seara asta la ora 23:59 se dă reset la balanța cash de pe Bolt, după care începe o nouă săptămână fiscală. 📈</b> 💱️

⚠️ Orice sumă <b>NU</b> e acoperită până în ora 23:59 <i>(miez de noapte către ziua de luni)</i> se va trage din următorul raport (<u><b>bani impozitabili</b></u>) - 👎

📌 Așadar, asigurați-vă că aveți balanța numerar pe 0 înainte de resetare, ca să nu existe probleme și confuzii. 👌✌️

📊 Țineți minte că, la Bolt, ar trebui să aveți balanța pe 0 la finalul zilei de duminică, săptămână de săptămână!

✅ Puteți face depunerea direct din aplicația Bolt Courier (actualizare în mai puțin de o oră). Dacă întâmpinați dificultăți cu depunerea, contactați asistența din aplicație -/- scrieți pe grupul Bolt/Suport General -/- cereți ajutorul unui helper.

🤝 Mulțumim de colaborare și un final de săptămână liniștit! 🙏🤍
"""

BOLT_MESSAGE_2 = """🚛 <b>BOLT – Reminder FINAL</b> ⏰

⚠️ <b>Atenție!</b>
Resetarea balanței cash la Bolt are loc la ora <b>23:59</b>, după care începe o nouă săptămână fiscală.

❗ Dacă mai aveți sume nedepuse:
➡️ vor fi trase din următorul raport
➡️ <u><b>bani impozitabili</b></u> ❌

📌 <b>Asigurați-vă că:</b>
• ați depus suma <b>integrală</b> până în ora <b>23:59</b>
• balanța este <b>0</b>

⛔ Nu lăsați pe ultima secundă!

🤝 Mulțumim pentru colaborare și înțelegere!
"""

GLOVO_MESSAGE_1 = """

🔄 <b>În seara asta la ora 23:59 se dă reset la balanța cash de pe Glovo, după care începe o nouă săptămână fiscală. 📈</b> 💱️

⚠️ Orice sumă <b>NU</b> e acoperită până în ora <b>23:59</b> <i>(miez de noapte către ziua de luni)</i> se va trage din următorul raport (<u><b>bani impozitabili</b></u>) - 👎

📌 Așadar, asigurați-vă că aveți balanța numerar pe 0 înainte de resetare, ca să nu existe probleme și confuzii. 👌✌️

📊 Nu uitați că la Glovo, resetarea poate fi decalată până în ora 14:00 din ziua de Luni (ține de platformă, nu de noi) - de aceea recomandăm să mențineți balanța sub pragul de <b>200</b> (pe minus) în acel interval pentru a nu vi se trage din raportul care urmează, și ulterior din plata pe acea săptămână.

✅ Puteți face depunerea direct prin <a href="https://www.selfpay.ro/localizare/">SelfPay</a> (actualizare instantă). Dacă întâmpinați dificultăți cu depunerea, contactați asistența din aplicație -/- scrieți pe grupul Glovo sau Suport General -/- cereți ajutorul unui helper.

🤝 Mulțumim de colaborare și un final de săptămână liniștit! 🙏🤍
"""

GLOVO_MESSAGE_2 = """🍔 <b>GLOVO – Reminder FINAL</b> ⏰

⚠️ <b>Atenție!</b>
Resetarea balanței cash la Glovo are loc la ora <b>23:59</b>, după care începe o nouă săptămână fiscală.

❗ Dacă mai aveți sume nedepuse:
➡️ vor fi trase din următorul raport
➡️ <u><b>bani impozitabili</b></u> ❌

📌 <b>Asigurați-vă că:</b>
• ați depus suma <b>integrală</b> până în ora <b>23:59</b>
• balanța este <b>0</b>

📊 Nu uitați că la Glovo, resetarea poate fi decalată până în ora 14:00 din ziua de Luni (ține de platformă, nu de noi) - de aceea recomandăm să mențineți balanța sub pragul de 200 în acel interval pentru a nu vi se trage din raportul care urmează, și ulterior din plata pe acea săptămână.

🤝 Mulțumim pentru colaborare și înțelegere - să aveți o încheiere de săptămână liniștită și la zi cu toate! 😌🙏
"""

WOLT_MESSAGE_1 = """

🔄 <b>În seara asta la ora 23:59 se dă reset la balanța cash de pe Wolt, după care începe o nouă săptămână fiscală. 📈</b> 💱

⚠️ Orice sumă <b>NU</b> e acoperită până în ora <b>23:59</b> <i>(miez de noapte către ziua de luni)</i> se va trage din următorul raport (<u><b>bani impozitabili</b></u>) - 👎

📌 Așadar, asigurați-vă că aveți balanța numerar pe 0 înainte de resetare, ca să nu existe probleme și confuzii. 👌✌️

✅ Puteți face depunerea direct prin <a href="https://youtube.com/shorts/p_dF5jPabLc?feature=share">Aircash</a> (actualizare instantă). Dacă întâmpinați dificultăți cu depunerea, contactați asistența din aplicație -/- scrieți pe grupul Wolt sau Suport General -/- cereți ajutorul unui helper.

📅 Țineți minte calendarul la Wolt pe care se calculează fiecare săptămână a lunii: <b>01–07 | 08–15 | 16–22 | 23–01</b>. Zilele în care se dă reset sunt: <b>01, 07, 15, 22</b>, în fiecare lună, la final de zi <b>(23:59)</b>.

🤝 Mulțumim de colaborare și un final de săptămână liniștit! 🙏🤍
"""

WOLT_MESSAGE_2 = """

⚠️ <b>Atenție!</b>
Resetarea balanței cash la Wolt are loc la ora <b>23:59</b>, după care începe o nouă săptămână fiscală.

❗ Dacă mai aveți sume nedepuse:
➡️ vor fi trase din următorul raport
➡️ <u><b>bani impozitabili</b></u> ❌

📌 <b>Asigurați-vă că:</b>
• ați depus suma <b>integrală</b> până în ora <b>23:59</b>
• balanța este <b>0</b>

⛔ Nu lăsați pe ultima secundă!

🤝 Mulțumim pentru colaborare și înțelegere!
"""

# =========================
# TELEGRAM HELPERS
# =========================

def telegram_api(method, data):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    response = requests.post(url, data=data, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def send_message(text, thread_id=None, auto_delete=False):
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    if thread_id is not None:
        data["message_thread_id"] = thread_id

    try:
        response = telegram_api("sendMessage", data)

        if not response.get("ok"):
            logger.error("Telegram sendMessage failed: %s", response)
            return

        message_id = response["result"]["message_id"]
        logger.info("Message sent successfully to thread %s", thread_id)

        if auto_delete:
            time.sleep(3)
            delete_message(message_id)

    except requests.RequestException as exc:
        logger.exception("Network error while sending message: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error while sending message: %s", exc)


def delete_message(message_id):
    try:
        response = telegram_api(
            "deleteMessage",
            {
                "chat_id": CHAT_ID,
                "message_id": message_id,
            }
        )

        if not response.get("ok"):
            logger.warning("Telegram deleteMessage failed: %s", response)

    except requests.RequestException as exc:
        logger.exception("Network error while deleting message: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error while deleting message: %s", exc)


# =========================
# SCHEDULER
# =========================

scheduler = BackgroundScheduler(timezone=TIMEZONE)


def add_production_jobs():
    scheduler.add_job(
        send_message,
        trigger="cron",
        day_of_week="sun",
        hour=12,
        minute=0,
        args=[BOLT_MESSAGE_1, BOLT_THREAD_ID, False],
        id="bolt_reminder_1",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="cron",
        day_of_week="sun",
        hour=22,
        minute=0,
        args=[BOLT_MESSAGE_2, BOLT_THREAD_ID, False],
        id="bolt_reminder_2",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="cron",
        day_of_week="sun",
        hour=12,
        minute=0,
        args=[GLOVO_MESSAGE_1, GLOVO_THREAD_ID, False],
        id="glovo_reminder_1",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="cron",
        day_of_week="sun",
        hour=22,
        minute=0,
        args=[GLOVO_MESSAGE_2, GLOVO_THREAD_ID, False],
        id="glovo_reminder_2",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="cron",
        day="1,7,15,22",
        hour=12,
        minute=0,
        args=[WOLT_MESSAGE_1, WOLT_THREAD_ID, False],
        id="wolt_reminder_1",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="cron",
        day="1,7,15,22",
        hour=22,
        minute=0,
        args=[WOLT_MESSAGE_2, WOLT_THREAD_ID, False],
        id="wolt_reminder_2",
        replace_existing=True,
    )

    logger.info("Production mode is ON: recurring reminders loaded")


def add_test_jobs():
    base_time = datetime.now().replace(second=0, microsecond=0)

    scheduler.add_job(
        send_message,
        trigger="date",
        run_date=base_time + timedelta(minutes=2),
        args=[BOLT_MESSAGE_1, BOLT_THREAD_ID, False],
        id="test_bolt_1",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="date",
        run_date=base_time + timedelta(minutes=4),
        args=[BOLT_MESSAGE_2, BOLT_THREAD_ID, False],
        id="test_bolt_2",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="date",
        run_date=base_time + timedelta(minutes=6),
        args=[GLOVO_MESSAGE_1, GLOVO_THREAD_ID, False],
        id="test_glovo_1",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="date",
        run_date=base_time + timedelta(minutes=8),
        args=[GLOVO_MESSAGE_2, GLOVO_THREAD_ID, False],
        id="test_glovo_2",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="date",
        run_date=base_time + timedelta(minutes=10),
        args=[WOLT_MESSAGE_1, WOLT_THREAD_ID, False],
        id="test_wolt_1",
        replace_existing=True,
    )

    scheduler.add_job(
        send_message,
        trigger="date",
        run_date=base_time + timedelta(minutes=12),
        args=[WOLT_MESSAGE_2, WOLT_THREAD_ID, False],
        id="test_wolt_2",
        replace_existing=True,
    )

    logger.info("TEST_MODE is ON: scheduled 6 test reminders in the next 12 minutes")


if TEST_MODE:
    add_test_jobs()
else:
    add_production_jobs()

# =========================
# CUSTOM ONE-TIME REMINDERS
# =========================

def schedule_custom(date_str, text, thread_id=None):
    try:
        try:
            run_date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
        except ValueError:
            run_date = datetime.strptime(date_str, "%d/%m/%Y %H:%M")

        scheduler.add_job(
            send_message,
            trigger="date",
            run_date=run_date,
            args=[text, thread_id, False],
        )

        logger.info("Custom reminder scheduled for %s in thread %s", date_str, thread_id)

    except ValueError:
        send_message(
            "⚠️ Format corect: /schedule 16-04-2026 05:00 mesaj",
            thread_id=thread_id,
            auto_delete=True,
        )
    except Exception as exc:
        logger.exception("Failed to schedule custom reminder: %s", exc)
        send_message(
            "⚠️ A apărut o eroare la programarea reminderului.",
            thread_id=thread_id,
            auto_delete=True,
        )

# =========================
# TELEGRAM UPDATES
# =========================

def handle_updates():
    global last_update_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 10}

    if last_update_id is not None:
        params["offset"] = last_update_id + 1

    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.exception("Network error while fetching updates: %s", exc)
        return
    except Exception as exc:
        logger.exception("Unexpected error while fetching updates: %s", exc)
        return

    for update in payload.get("result", []):
        last_update_id = update["update_id"]

        message = update.get("message", {})
        text = message.get("text", "")
        message_id = message.get("message_id")
        user_id = message.get("from", {}).get("id")
        thread_id = message.get("message_thread_id")

        if not text.startswith("/schedule"):
            continue

        if user_id not in ADMIN_IDS:
            logger.warning("Unauthorized /schedule attempt by user %s", user_id)
            continue

        parts = text.split(" ", 3)

        if len(parts) < 4:
            send_message(
                "⚠️ Format corect: /schedule 16-04-2026 05:00 mesaj",
                thread_id=thread_id,
                auto_delete=False,
            )
            continue

        try:
            delete_message(message_id)
        except Exception:
            logger.warning("Could not delete admin command message %s", message_id)

        date_part = parts[1]
        time_part = parts[2]
        msg_part = parts[3]

        schedule_custom(f"{date_part} {time_part}", msg_part, thread_id)

# =========================
# START
# =========================

def main():
    scheduler.start()
    logger.info("Bot is running with timezone %s", TIMEZONE)

    try:
        while True:
            handle_updates()
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
