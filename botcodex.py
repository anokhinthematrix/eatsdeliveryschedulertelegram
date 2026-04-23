import logging
import os
import time
from datetime import datetime

import requests
from apscheduler.schedulers.background import BackgroundScheduler

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ADMIN_IDS = [804349433, 8711909473]

BOLT_THREAD_ID = 10
GLOVO_THREAD_ID = 12
WOLT_THREAD_ID = 6

TIMEZONE = "Europe/Bucharest"
POLL_INTERVAL_SECONDS = 2
REQUEST_TIMEOUT = 15

TEST_MODE = False

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

⚠ Orice sumă <b>NU</b> e acoperită până în ora 23:59 <i>(miez de noapte către ziua de luni)</i> se va trage din următorul raport (<u><b>bani impozitabili</b></u>) - 👎

📌 Așadar, asigurați-vă că aveți balanța numerar pe 0 înainte de resetare, ca să nu existe probleme și confuzii. 👌✌️

📊 Țineți minte că, la Bolt, ar trebui să aveți balanța pe 0 la finalul zilei de duminică, săptămână de săptămână!

✅ Puteți face depunerea direct din aplicația <a href="https://youtube.com/shorts/5d296X-pYqk?feature=share">Bolt Courier</a> (actualizare în mai puțin de o oră). Dacă întâmpinați dificultăți cu depunerea, contactați asistența din aplicație -/- scrieți pe grupul Bolt/Suport General -/- cereți ajutorul unui helper.

🤝 Mulțumim de colaborare și un final de săptămână liniștit! 🙏🤍



🇺🇸 EN:

🔄 <b>Tonight at 23:59 the cash balance on Bolt will be reset, after which a new fiscal week begins. 📈</b> 💱️

⚠ Any amount <b>NOT</b> covered by 23:59 <i>(midnight to Monday)</i> will be deducted from the next report (<u><b>taxable money</b></u>) - 👎

📌 Therefore, make sure your cash balance is 0 before the reset, so there are no issues and confusion. 👌✌️

📊 Keep in mind that, on Bolt, you should have your balance at 0 at the end of Sunday, on a weekly basis!

✅ You can make the deposit directly from the <a href="https://youtube.com/shorts/5d296X-pYqk?feature=share">Bolt Courier App</a> (updated in less than an hour). If you encounter difficulties with the deposit, contact support in the app -/- write in the Bolt/General Support group -/- ask a helper for assistance.

🤝 Thank you for your collaboration and have a peaceful end of the week! 🙏🤍
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



🇺🇸 EN:

⚠️ <b>Attention!</b>
The cash balance reset at Bolt takes place at <b>23:59</b>, after which a new fiscal week begins.

❗ If you still have a negative cash balance by the end of the day:
➡️ they will be deducted from the next report
➡️ <u><b>taxable money</b></u> ❌

📌 <b>Make sure that:</b>
• you have deposited the <b>full amount</b> by <b>23:59</b>
• the balance is <b>0</b>

⛔ Do not leave it to the last second!

🤝 Thank you for your collaboration and understanding!
"""

GLOVO_MESSAGE_1 = """

🔄 <b>În seara asta la ora 23:59 se dă reset la balanța cash de pe Glovo, după care începe o nouă săptămână fiscală. 📈</b> 💱️

⚠ Orice sumă <b>NU</b> e acoperită până în ora <b>23:59</b> <i>(miez de noapte către ziua de luni)</i> se va trage din următorul raport (<u><b>bani impozitabili</b></u>) - 👎

📌 Așadar, asigurați-vă că aveți balanța numerar pe 0 înainte de resetare, ca să nu existe probleme și confuzii. 👌✌️

📊 Nu uitați că la Glovo, resetarea poate fi decalată până în ora 14:00 din ziua de Luni (ține de platformă, nu de noi) - de aceea recomandăm să mențineți balanța sub pragul de <b>200</b> (pe minus) în acel interval pentru a nu vi se trage din raportul care urmează, și ulterior din plata pe acea săptămână.

✅ Puteți face depunerea direct prin <a href="https://www.selfpay.ro/localizare/">SelfPay</a> (actualizare instantă). Dacă întâmpinați dificultăți cu depunerea, contactați asistența din aplicație -/- scrieți pe grupul Glovo sau Suport General -/- cereți ajutorul unui helper.

🤝 Mulțumim de colaborare și un final de săptămână liniștit! 🙏🤍



🇺🇸 EN:

🔄 <b>Tonight at 23:59 the cash balance on Glovo will be reset, after which a new fiscal week begins. 📈</b> 💱️

⚠ Any amount <b>NOT</b> covered by <b>23:59</b> <i>(midnight to Monday)</i> will be deducted from the next report (<u><b>taxable money</b></u>) - 👎

📌 Therefore, make sure your cash balance is 0 before the reset, so there are no issues or confusion. 👌✌️

📊 Do not forget that at Glovo, the reset may be delayed until 14:00 on Monday (this depends on the platform, not on us) – therefore we recommend keeping the balance below the threshold of <b>200</b> (negative) during that interval to avoid having amounts deducted from the upcoming report, and later from that week’s payment.

✅ You can make the deposit directly via <a href="https://www.selfpay.ro/localizare/">SelfPay</a> (instant update). If you encounter difficulties with the deposit, contact support in the app -/- write in the Glovo group or General Support -/- ask a helper for assistance.

🤝 Thank you for your collaboration and have a peaceful end of the week! 🙏🤍
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



🇺🇸 EN:

⚠️ <b>Attention!</b>
The cash balance reset at Glovo takes place at <b>23:59</b>, after which a new fiscal week begins.

❗ If you still have a negative cash balance by the end of the day:
➡️ they will be deducted from the next report
➡️ <u><b>taxable money</b></u> ❌

📌 <b>Make sure that:</b>
• you have deposited the <b>full amount</b> by <b>23:59</b>
• the balance is <b>0</b>

📊 Do not forget that at Glovo, the reset may be delayed until 14:00 on Monday (this depends on the platform, not on us) – therefore we recommend keeping the balance below 200 during that interval to avoid having amounts deducted from the upcoming report, and later from that week’s payment.

🤝 Thank you for your collaboration and understanding – have a calm end of the week, and up to date with everything! 😌🙏

"""

WOLT_MESSAGE_1 = """

🔄 <b>În seara asta la ora 23:59 se dă reset la balanța cash de pe Wolt, după care începe o nouă săptămână fiscală. 📈</b> 💱

⚠ Orice sumă <b>NU</b> e acoperită până în ora <b>23:59</b> <i>(miez de noapte către următoarea zi)</i> se va trage din următorul raport (<u><b>bani impozitabili</b></u>) - 👎

📌 Așadar, asigurați-vă că aveți balanța numerar pe 0 înainte de resetare, ca să nu existe probleme și confuzii. 👌✌️

✅ Puteți face depunerea direct prin <a href="https://youtube.com/shorts/p_dF5jPabLc?feature=share">Aircash</a> (actualizare instantă). Dacă întâmpinați dificultăți cu depunerea, contactați asistența din aplicație -/- scrieți pe grupul Wolt sau Suport General -/- cereți ajutorul unui helper.

📅 Țineți minte calendarul la Wolt pe care se calculează fiecare săptămână fiscală a lunii: <b>01–07 | 08–15 | 16–22 | 23–01</b>. Zilele în care se dă reset sunt: <b>01, 07, 15, 22</b>, în fiecare lună, la final de zi <b>(23:59)</b>.

✋ Încă un lucru important de reținut (știm, v-au zăpăcit și pe voi, și pe noi 😅): La Wolt, în zilele 2-8-16-23 (cu o zi după reset) nu faceți nicio depunere, altfel se trage de două ori (și din raport, și depunerea voastră).

🤝 Mulțumim de colaborare și o zi cu spor! 🙏🤍



🇺🇸 EN:

🔄 <b>Tonight at 23:59 the cash balance on Wolt will be reset, after which a new fiscal week begins. 📈</b> 💱

⚠ Any amount <b>NOT</b> covered by <b>23:59</b> <i>(midnight to the following day)</i> will be deducted from the next report (<u><b>taxable money</b></u>) - 👎

📌 Therefore, make sure your cash balance is 0 before the reset, so there are no issues or confusion. 👌✌️

✅ You can make the deposit directly via <a href="https://youtube.com/shorts/p_dF5jPabLc?feature=share">Aircash</a> (instant update). If you encounter difficulties with the deposit, contact support in the app -/- write in the Wolt group or General Support -/- ask a helper for assistance.

📅 Keep in mind the Wolt schedule used to calculate each fiscal week of the month: <b>01–07 | 08–15 | 16–22 | 23–01</b>. The reset days are: <b>01, 07, 15, 22</b>, every month, at the end of the day <b>(23:59)</b>.

✋ One more important thing to remember (we know, it’s confusing for both you and us 😅): At Wolt, on days 2-8-16-23 (one day after the reset) do not make any deposit, otherwise it will be deducted twice (both from the report and your deposit).

🤝 Thank you for your collaboration and have a productive day! 🙏🤍
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
• nu depuneți în ziua următoare (banii pot fi opriți de 2 ori)

⛔ Nu lăsați pe ultima secundă!

🤝 Mulțumim pentru colaborare și înțelegere - o seară liniștită! 🙏🤍



🇺🇸 EN:

⚠️ <b>Attention!</b>
The cash balance reset at Wolt takes place at <b>23:59</b>, after which a new fiscal week begins.

❗ If you still have a negative cash balance by the end of the day:
➡️ they will be deducted from the next report
➡️ <u><b>taxable money</b></u> ❌

📌 <b>Make sure that:</b>
• you have deposited the <b>full amount</b> by <b>23:59</b>
• the balance is <b>0</b>
• you do not deposit on the following day (the money could be deducted twice)

⛔ Do not leave it to the last second!

🤝 Thank you for your collaboration and understanding – have a peaceful evening! 🙏🤍
"""

GLOVO_CALENDAR_JOI = """

🍔 <b>GLOVO - Orele disponibile pentru o nouă săptămână vor fi disponibile în curând în aplicație! </b>⏰

📌 Calendarul la Glovo se actualizează în fiecare Joi și va fi disponibil de astăzi, pentru toată săptămâna viitoare, Luni-Duminică.

🏅 În funcție de nivelul pe care îl aveți la Glovo, asta va determina și ora la care veți avea acces la calendar:

Nivelul 1 - 16:00
Nivelul 2 - 16:30
Nivelul 3 - 17:00
Nivelul 4 - 17:30
Nivelul 5 - 18:00
Nivelul 6 - 18:30
Nivelul 7 - 19:00
Nivelul 8 - 19:30
Nivelul 9 - 20:00
Nivelul 10 - 20:30
Nivelul 11 - 18:00
Nivelul 12 - 21:00
Nivelul Diamant - 15:00
Nivel Gold - 16:00

❗ <b>selectați doar intervalele pe care știți sigur că le puteți realiza;</b>
❗ <b>nu lăsați orele de rezervare pe ultimul moment - fiind o perioadă destul de aglomerată și mulți curieri activi, riscați să nu prindeți orele dorite mai târziu.</b>



🇺🇸 EN:

🍔 <b>GLOVO - The schedule (available hours) for the next week will soon be available in the app! </b>⏰

📌 At Glovo, the schedule is updated every Thursday and will be available starting today, for the entire next week, Monday–Sunday.

🏅 Depending on your level in the Glovo app, this will also determine the hour at which you will have access to the schedule:

Level 1 - 16:00
Level 2 - 16:30
Level 3 - 17:00
Level 4 - 17:30
Level 5 - 18:00
Level 6 - 18:30
Level 7 - 19:00
Level 8 - 19:30
Level 9 - 20:00
Level 10 - 20:30
Level 11 - 18:00
Level 12 - 21:00
Diamond Level - 15:00
Gold Level - 16:00

❗ <b>select only the time slots that you are sure you can complete;</b>
❗ <b>do not leave booking hours to the last moment – as it is a fairly busy period with many active couriers, you risk not having your desired hours available later.</b>
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

    scheduler.add_job(
        send_message,
        trigger="cron",
        day_of_week="thu",
        hour=15,
        minute=50,
        args=[GLOVO_CALENDAR_JOI, GLOVO_THREAD_ID, False],
        id="thursday_reminder",
        replace_existing=True,
    )

    logger.info("Production mode is ON: recurring reminders loaded")


if not TEST_MODE:
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
