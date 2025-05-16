import os
import yaml
from pathlib import Path

def setup_email_credentials():
    """Interactive setup for email credentials."""
    print("Setting up email credentials...")
    
    # Get email address
    email = input("Enter your email address: ").strip()
    
    # Get password
    print("\nFor Gmail users:")
    print("1. Go to your Google Account settings")
    print("2. Enable 2-Step Verification if not already enabled")
    print("3. Go to Security → App passwords")
    print("4. Generate a new app password for 'Mail'")
    print("5. Copy the generated password")
    password = input("\nEnter your app password: ").strip()
    
    # Create user config directory if it doesn't exist
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create or update user config
    user_config = {
        "integrations": {
            "email": {
                "username": email,
                "password": password
            }
        }
    }
    
    # Save to user_config.yaml
    config_path = config_dir / "user_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(user_config, f, default_flow_style=False)
    
    print(f"\nConfiguration saved to {config_path}")
    print("You can now run test_email.py to test the email functionality")

if __name__ == "__main__":
    setup_email_credentials() 