# config.py
# IMPORTANT: Never commit sensitive data into version control. 
# This token should be retrieved from a secure location such as environment variables or a secrets manager.

# Example of how you might set the AUTH_TOKEN from an environment variable
import os

AUTH_TOKEN = os.getenv('CHALLENGE_SERVER_AUTH_TOKEN')
CHALLENGE_SERVER_BASE_URL = 'https://api.cloudkitchens.com'
