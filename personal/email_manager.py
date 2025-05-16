"""
Email manager module for handling email communications.
"""

import logging
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email

class EmailManager:
    """Manages email communications and notifications."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        imap_server: str,
        imap_port: int,
        username: str,
        password: str
    ):
        """Initialize email manager with server configuration."""
        self.logger = logging.getLogger(__name__)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.username = username
        self.password = password
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> None:
        """Send an email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise
    
    def get_emails(
        self,
        folder: str = "INBOX",
        limit: int = 10,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get emails from a folder."""
        try:
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as imap:
                imap.login(self.username, self.password)
                imap.select(folder)
                
                search_criteria = "(UNSEEN)" if unread_only else "ALL"
                _, message_numbers = imap.search(None, search_criteria)
                
                emails = []
                for num in message_numbers[0].split()[-limit:]:
                    _, msg_data = imap.fetch(num, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    emails.append({
                        'subject': email_message['subject'],
                        'from': email_message['from'],
                        'date': email_message['date'],
                        'body': self._get_email_body(email_message)
                    })
                
                return emails
                
        except Exception as e:
            self.logger.error(f"Failed to get emails: {e}")
            raise
    
    def _get_email_body(self, email_message: email.message.Message) -> str:
        """Extract email body from message."""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        return email_message.get_payload(decode=True).decode() 