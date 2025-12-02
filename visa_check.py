import os
import json
import smtplib
from email.mime.text import MIMEText
from urllib.request import urlopen

from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import json
import os
import smtplib
from email.mime.text import MIMEText

STATUS_URL = "https://ipc.gov.cz/api/ip/external/proceedings/state/cj/zov?idCj=71164&database=ZM&year=2025&zov="
EXPECTED_STATE = "INPROGRESS"


def get_current_state():
    try:
        req = Request(
            STATUS_URL,
            headers={
                # pretend to be a normal browser
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
            },
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("state"), data.get("identification")
    except HTTPError as e:
        print(f"HTTPError when calling status URL: {e.code} {e.reason}")
        return None, None
    except URLError as e:
        print(f"URLError when calling status URL: {e.reason}")
        return None, None


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

