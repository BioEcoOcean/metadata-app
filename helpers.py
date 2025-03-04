# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()


def set_flask_environment(app) -> str:
    """Set the flask development environment.
    Parameters
    ----------
    app: flask.Flask
        The flask application object
    Raises
    ------
    KeyError
        If the FLASK_ENV environment variable is not set.
    Returns
    -------
    str:
        Flask operating environment i.e development
    """
    if os.environ['FLASK_ENV'] == 'production':  # pragma: no cover
        app.config.from_object('config.ProductionConfig')
    elif os.environ['FLASK_ENV'] == 'development':  # pragma: no cover
        app.config.from_object('config.DevelopmentConfig')
    elif os.environ['FLASK_ENV'] == 'test':
        app.config.from_object('config.TestingConfig')

    return os.environ['FLASK_ENV']