from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
import googleapiclient.errors as errors

from oauth2client import file, client, tools
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import base64

testmes = ""
testmes += "<p>Hi,</p>"
testmes += "<p>This is a test.</p>"
testmes += "<p>Kind regards,</p>"
testmes += "<p>Peter</p>"



def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    # Load the image you want to send as bytes
    img_data = open('logo.jpg', 'rb').read()

    # Create a "related" message container that will hold the HTML 
    # message and the image. These are "related" (not "alternative")
    # because they are different, unique parts of the HTML message,
    # not alternative (html vs. plain text) views of the same content.
    html_part = MIMEMultipart(_subtype='related')

    # Create the body with HTML. Note that the image, since it is inline, is 
    # referenced with the URL cid:myimage... you should take care to make
    # "myimage" unique
    body = MIMEText('<div>' + testmes + '<img src="cid:myimage" /></div>', _subtype='html')
    html_part.attach(body)

    # Now create the MIME container for the image
    img = MIMEImage(img_data, 'jpeg')
    img.add_header('Content-Id', '<myimage>')  # angle brackets are important
    img.add_header("Content-Disposition", "inline", filename="myimage")
    # David Hess recommended this edit
    html_part.attach(img)

    #the html part is already has what we need in MIMEMultipart format

    #message = MIMEText(message_text)
    html_part['to'] = to
    html_part['from'] = sender
    html_part['subject'] = subject
    return { 'raw' : base64.urlsafe_b64encode(html_part.as_bytes()).decode() }

def send_message(service, user_id, message):
    """Send an email message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """

    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message

    except errors.HttpError as error:
        print('An error occurred: %s' % error)

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.send'

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    #create test message
    msg = create_message("imnotreal@gmail.com","peter@os3.nl","bot_test",testmes)
    #Call the Gmail API, and send message
    #return any errors
    send_message(service,"me", msg)

if __name__ == '__main__':
    main()
