# Bot token
TOKEN = '<TOKEN>'
ROOT_UID = 61043901

LOGGING_TO_CHAT = True
CHAT_ID = 0

# Time zone and locale settings
TIMEZONE = 'Europe/Kiev'
DEFAULT_LOCALE = 'en_US'

# Ignore unread messages on startup
IGNORE_UNREAD_MESSAGES = True

# Debugging
DEBUG = True

# Karma settings
ANTI_FLOOD_TIMEOUT = 2

# === WebHook ===
# Notice: Use webhook in production.
# If disabled - web server and statistic will be not work.
USE_WEBHOOK = False
# Domain name
WEBHOOK_URL = 'telekarma.example.com'

# SSL
# For example use Free signed LetsEncrypt SSL certificate.

# Path to the ssl certificate
WEBHOOK_SSL_CERT = '/etc/letsencrypt/live/%s/cert.pem' % WEBHOOK_URL
# Path to the ssl private key
WEBHOOK_SSL_PRIV = '/etc/letsencrypt/live/%s/privkey.pem' % WEBHOOK_URL

# === Web server settings ===
# host & port
WEB_HOST = '0.0.0.0'
WEB_PORT = 37529
