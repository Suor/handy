INSTALLED_APPS = [
    'tests',
]

# Django replaces this, but it still wants it. *shrugs*
DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2',
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'handy',
        'USER': 'handy',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        # 'OPTIONS': {"autocommit": True},
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]

TIME_ZONE = 'Asia/Krasnoyarsk'

SECRET_KEY = 'abc'
