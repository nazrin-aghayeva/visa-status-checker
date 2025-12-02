import os
import json
import smtplib
from email.mime.text import MIMEText
from urllib.request import urlopen

STATUS_URL = "https://ipc.gov.cz/api/ip/external/proceedings/state/cj/zov?idCj=71164&database=ZM&year=2025&zov="
EXPECTED_STATE = "INPROGRESS"


def get_current_state():
    with urlopen(STATUS_URL, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("state"), data.get("identification")


def send_email(subject, body):
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    email_from = os.environ["EMAIL_FROM"]
    email_to = os.environ["EMAIL_TO"]

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def main():
    state, identification = get_current_state()

    if state is None:
        # something went wrong, just exit quietly
        return

    # If state is NOT INPROGRESS -> send email
    if state != EXPECTED_STATE:
        subject = f"Visa status changed: {identification} -> {state}"
        body = (
            f"Your application {identification} is no longer in state {EXPECTED_STATE}.\n\n"
            f"Current state: {state}\n\n"
            f"Checked URL:\n{STATUS_URL}\n\n"
            f"(This check is run by GitHub Actions.)"
        )
        send_email(subject, body)


if __name__ == "__main__":
    main()

