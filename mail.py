import smtplib, ssl
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from os.path import basename

from utils import get_day_name
from utils import get_mail_credentials
from utils import make_date_string

#TODO: Only imported for testing purposes
import datetime as dt
from utils import load_history
from utils import filter_history


def send_message(receiver, subject, text, html=None, attachments=None):
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
            with open(attachment, 'r') as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(attachment)
                )
            part['Content-Disposition'] = f'attachment; filename="{basename(attachment)}"'
            message.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email,
            receiver,
            message.as_string()
        )


def send_recommendations(receivers, recommendations, shopping_list_file=None):
    dates = list(recommendations.keys())

    min_date_str = make_date_string(min(dates))
    max_date_str = make_date_string(max(dates))

    # Create the plain-text and HTML version of your message
    text = f'Meal recommendations for {min_date_str} to {max_date_str} are as follows:\n'

    sorted_dates = sorted(list(recommendations.keys()))
    for date in sorted_dates:
        meal = recommendations[date]
        date_str = make_date_string(date)
        text += f'\n{date_str} - {str(meal)}'

    text += "\n\nBon Appetit!\nMeal Prep Team\n"

    subject = f'Meal Recommendations {min(dates).strftime("%d/%m/%Y")} - {max(dates).strftime("%d/%m/%Y")}'

    if shopping_list_file is not None:
        attachments = [shopping_list_file]
    else:
        attachments = None

    if isinstance(receivers, str):
        receivers = [receivers]

    for receiver in receivers:
        send_message(receiver, subject, text, attachments=attachments)


if __name__ == '__main__':
    history = load_history(start=dt.date.today())
    shopping_list = 'lists/shopping_list_20201126_20201205.txt'
    send_recommendations(
        'mealprepbot@gmail.com',
        history,
        shopping_list_file = shopping_list
    )
