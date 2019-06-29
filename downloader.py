#!/usr/bin/env python3
import os
import base64
import pickle
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.pickle'
SECRET_FILE = 'credentials.json'

def get_service():
    """
    Log in to Gmail with credentials and return a service.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                SECRET_FILE, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service


def search_emails(service, user_id='me', query=''):
    """
    Search gmail and find emails with matching query.
    """
    response = service.users().messages().list(
        userId=user_id,
        q=query
        ).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(
            userId=user_id,
            q=query,
            pageToken=page_token
            ).execute()
        messages.extend(response['messages'])
    return messages


def get_attachments(service, msg_id, store_dir, user_id='me', use_sub=False):
    """
    Get and store attachment from email with given id.
    """
    message = service.users().messages().get(
        userId=user_id,
        id=msg_id
        ).execute()

    for part in message.get('payload', {}).get('parts', []):
        fname = part['filename']
        if fname:
            print("Downloading file {}".format(fname))
            data = part['body'].get('data', '')
            if not data:
                attachment_id = part['body']['attachmentId']
                attachment = service.users().messages().attachments().get(
                    userId=user_id,
                    messageId=msg_id,
                    id=attachment_id
                    ).execute()
                data = attachment['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            if use_sub:
                fname = '-'.join(
                    [get_message_subject(message.get('payload', {})), fname])
            path = os.path.join(store_dir, fname)
            with open(path, 'wb') as f:
                f.write(file_data)
            print('Wrote data to {}'.format(path))


def get_message_subject(payload):
    """
    Get subject of an email from message payload.
    """
    subject = ''
    headers = payload.get('headers', [])
    if headers:
        for header in headers:
            if header.get('name') != 'Subject':
                continue
            subject = header.get('value')
    return subject


def parse_args():
    parser = argparse.ArgumentParser(description='Arguments for downloader')
    parser.add_argument(
        'query',
        metavar='Q',
        type=str,
        help='Query to filter emails')
    parser.add_argument(
        'store_dir',
        metavar='D',
        type=str,
        help='Directory path to store downloaded attachment files')
    parser.add_argument(
        '--use-sub',
        dest='use_sub',
        action='store_true',
        help='Flag to indicate whether to use email subject as file name')
    return parser.parse_args()


def main():
    args = parse_args()
    query = args.query
    store_dir = args.store_dir
    use_sub = args.use_sub

    # Start the downloader
    service = get_service()
    messages = search_emails(service, query=query)
    print('Found {} messages'.format(len(messages)))
    for msg in messages:
        get_attachments(service, msg.get('id', ''), store_dir, use_sub=use_sub)


if __name__ == '__main__':
    main()


