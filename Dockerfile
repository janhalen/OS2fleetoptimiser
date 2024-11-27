FROM python:3.10.4-bullseye

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /fleetmanager

RUN apt-get update &&\
    apt-get install -y unixodbc iproute2 unixodbc-dev gnupg curl libxml2-dev libpq-dev libxslt-dev libxmlsec1-dev &&\
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - &&\
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list &&\
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools &&\
    pip install poetry==1.3.1

# requiered libraries for pypeeter scraping of wltp etc. fleetmanager.extractors.util.load_content
RUN apt-get install -y \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libcups2 \
    libdbus-1-3 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0

COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev
ADD fleetmanager ./fleetmanager

RUN poetry install --only-root

RUN ["/bin/sh", "-c", "pytest -k fleetmanager/tests/"]
