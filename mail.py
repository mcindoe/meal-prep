import smtplib, ssl
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from os.path import basename

from utils import DAYS
from utils import get_mail_credentials

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


def get_date_str(date):
    day_name = DAYS[date.weekday()]
    day = date.day
    final_day_num = int(str(day)[-1])

    if final_day_num == 1:
        day_suffix = 'st'
    elif final_day_num == 2:
        day_suffix = 'nd'
    elif final_day_num == 3:
        day_suffix = 'rd'
    else:
        day_suffix = 'th'

    return f'{day_name}, {day}{day_suffix}'

def send_recommendations(receiver, recommendations, attachments=None):
    dates = list(recommendations.keys())
    
    min_date_str = get_date_str(min(dates))
    max_date_str = get_date_str(max(dates))

    sorted_dates = sorted(list(recommendations.keys()))

    # Create the plain-text and HTML version of your message
    text = f'Meal recommendations for {min_date_str} to {max_date_str} are as follows:\n'

    for date in sorted_dates:
        day_name = DAYS[date.weekday()]
        meal = recommendations[date]
        text += f'\n{day_name} - {meal}'

    text += "\n\nRegards,\nMeal Prep Team\n"

    subject = 'Meal Recommendations'
    send_message(receiver, subject, text, attachments=attachments)


if __name__ == '__main__':
    history = load_history()
    history = filter_history(history, start=dt.date(2020, 11, 8))
    shopping_list = 'Shopping List.txt'
    send_recommendations(
        'mealprepbot@gmail.com',
        history,
        attachments = [shopping_list]
    )
