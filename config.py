import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH   = os.path.join(BASE_DIR, 'data', 'messages.db')

SECRET_KEY      = 'a-very-secret-key-1234567890'
ADMIN_PASSWORD  = '12345'
RATE_LIMIT_SEC  = 10          # 提交间隔
COOKIE_MAX_AGE  = 60 * 60 * 24 * 365   # 1 年