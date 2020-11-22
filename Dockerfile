FROM python:3

WORKDIR /work

RUN apt-get update && \
    apt-get install -y \
    locales vim less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    locale-gen en_US.UTF-8 && \
    localedef -f UTF-8 -i en_US en_US.UTF-8

ENV TZ=UTC \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

RUN python -m pip install --upgrade pip && \
    python -m pip install --upgrade setuptools && \
    python -m pip install requests && \
    python -m pip install beautifulsoup4 && \
    python -m pip install selenium && \
    python -m pip install urllib3 && \
    python -m pip install csvkit
