"""
Provides email support and project-specific email functions such as
emailing meal recommendations
"""

import datetime as dt
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
from pathlib import Path
import smtplib
import ssl
from typing import Dict, List, Optional, Tuple

from mealprep.config import DATA
from mealprep.src.utils.display import make_date_string


MAIL_CREDENTIALS_FILE = DATA / "mail_credentials.txt"


def get_mail_credentials() -> Tuple[str, str]:
    """
    Fetch mail username, password from file

    :return: tuple of username, password
    """

    with open(MAIL_CREDENTIALS_FILE, "r") as fp:
        lines = fp.readlines()
    username, password = (line.rstrip("\n") for line in lines)
    return username, password


def send_message(
    receiver: str,
    subject: str,
    text: str,
    html: Optional[str] = None,
    attachments: Optional[List[Path]] = None,
) -> None:
    """
    Provides functionality to send an email from the project email
    address, as specified in the mail_credentils file.
    """

    sender_email, sender_password = get_mail_credentials()

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver
    message["Date"] = formatdate(localtime=True)

    message.attach(MIMEText(text, "plain"))

    if html is not None:
        message.attach(MIMEText(html, "html"))

    if attachments is not None:
        for attachment in attachments:
            with open(attachment, "r") as fil:
                part = MIMEApplication(fil.read(), Name=basename(attachment))
            part["Content-Disposition"] = f'attachment; filename="{basename(attachment)}"'
            message.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, message.as_string())


def send_recommendations(
    receivers: List[str],
    recommendations: Dict[dt.date, str],
    shopping_list_file: Optional[Path] = None,
) -> None:
    """
    Send the meal recommendations specified to each member of receivers,
    neatly formatted. Option to attach a shopping list to each email.
    """

    dates = list(recommendations.keys())

    min_date_str = make_date_string(min(dates))
    max_date_str = make_date_string(max(dates))

    # Create the plain-text and HTML version of your message
    text = f"Meal recommendations for {min_date_str} to " f"{max_date_str} are as follows:\n"

    sorted_dates = sorted(list(recommendations.keys()))
    for date in sorted_dates:
        meal = recommendations[date]
        date_str = make_date_string(date)
        text += f"\n{date_str} - {str(meal)}"

    text += "\n\nBon Appetit!\nMeal Prep Team\n"

    subject = (
        f"Meal Recommendations {min(dates).strftime('%d/%m/%Y')} - "
        f"{max(dates).strftime('%d/%m/%Y')}"
    )

    if shopping_list_file is not None:
        attachments = [shopping_list_file]
    else:
        attachments = None

    if isinstance(receivers, str):
        receivers = [receivers]

    for receiver in receivers:
        send_message(receiver, subject, text, attachments=attachments)
