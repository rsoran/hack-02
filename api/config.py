import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-mindease-key-change-in-production')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
