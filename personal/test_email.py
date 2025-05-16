import yaml
from email_manager import EmailManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from files."""
    try:
        with open('config/default_config.yaml', 'r') as f:
            default_config = yaml.safe_load(f)
        with open('config/user_config.yaml', 'r') as f:
            user_config = yaml.safe_load(f)
        
        # Merge configurations
        email_config = {**default_config['integrations']['email'], **user_config['integrations']['email']}
        return email_config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def main():
    try:
        # Load configuration
        email_config = load_config()
        
        # Initialize email manager
        email_manager = EmailManager(
            smtp_server=email_config['smtp_server'],
            smtp_port=email_config['smtp_port'],
            imap_server=email_config['imap_server'],
            imap_port=email_config['imap_port'],
            username=email_config['username'],
            password=email_config['password']
        )
        
        # Test sending an email
        logger.info("Testing email sending...")
        email_manager.send_email(
            to=email_config['username'],  # Send to self for testing
            subject="Test Email from Jarvis",
            body="This is a test email from Jarvis. If you receive this, the email system is working!"
        )
        logger.info("Email sent successfully!")
        
        # Test receiving emails
        logger.info("Testing email receiving...")
        emails = email_manager.get_emails(
            folder=email_config['default_folder'],
            limit=email_config['max_emails'],
            unread_only=email_config['unread_only']
        )
        
        logger.info(f"Found {len(emails)} emails")
        for email in emails:
            logger.info(f"Subject: {email['subject']}")
            logger.info(f"From: {email['from']}")
            logger.info(f"Date: {email['date']}")
            logger.info("---")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    main() 