#!/usr/bin/env bash
uv init
uv add flask
uv add pymongo
uv add flask-login
uv add python-dotenv
uv add gunicorn
uv sync
