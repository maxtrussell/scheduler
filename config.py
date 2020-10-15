import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DISCORD_USERNAME = "DnD Bot"
    DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/766149946797457459/CgTWyX7GqRod1RRxEqAZg3FqdaPxNhf6HxHg_lH8i45Uv7JOvSI6eAlFdBXoH6lrYhzw'
    DM_USER = 'max'
    QUORUM_THRESHOLD = 3
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
