import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

email_sender_password = os.getenv('email_sender_password')
sender_email = "spa.detente.france@gmail.com"
receiver_email = "mouss42490@gmail.com"

message = MIMEMultipart("alternative")
message["Subject"] = "multipart test"
message["From"] = sender_email
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = """\
Hi,
How are you?
Real Python has many great tutorials:
www.realpython.com"""
html = """\
<html>
  <body>
    <p>Hi,<br>
       How are you?<br>
       <a href="http://www.realpython.com">Real Python</a>
       has many great tutorials.
    </p>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

# Create secure connection with server and send email
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, email_sender_password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )






# import os
# from twilio.rest import Client
#
#
# # Find your Account SID and Auth Token at twilio.com/console
# # and set the environment variables. See http://twil.io/secure
#
# account_sid = os.environ['TWILIO_ACCOUNT_SID']
# auth_token = os.environ['TWILIO_AUTH_TOKEN']
#
# client = Client(account_sid, auth_token)
#
# message = client.messages \
#                 .create(
#                      body="Join Earth's mightiest heroes. Like Kevin Bacon.",
#                      from_='+16467624271',
#                      to='+33651323494'
#                  )
#
# print(message.sid)
