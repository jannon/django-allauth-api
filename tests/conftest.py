def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
       TEMPLATE_CONTEXT_PROCESSORS = (
            'django.contrib.auth.context_processors.auth',
            # Required by allauth template tags
            'django.core.context_processors.request',
        
            # allauth specific context processors
            'allauth.account.context_processors.account',
            'allauth.socialaccount.context_processors.socialaccount',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'allauth',
            'allauth.account',
            'allauth.socialaccount',
            'allauth.socialaccount.providers.facebook',
    
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.SHA1PasswordHasher',
            'django.contrib.auth.hashers.PBKDF2PasswordHasher',
            'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
            'django.contrib.auth.hashers.BCryptPasswordHasher',
            'django.contrib.auth.hashers.MD5PasswordHasher',
            'django.contrib.auth.hashers.CryptPasswordHasher',
        ),
    )

    try:
        import rest_framework
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += (
            'rest_framework',
            'rest_framework.authtoken',
        )

    try:
        import tastypie
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += (
            'tastypie',
        )

    try:
        import oauth_provider  # NOQA
        import oauth2  # NOQA
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += (
            'oauth_provider',
        )

    try:
        import oauth2_provider  # NOQA
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += (
            'oauth2_provider',
        )
    

    try:
        import django
        django.setup()
    except AttributeError:
        pass
    