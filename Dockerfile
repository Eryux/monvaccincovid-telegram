# Start from python alpine
FROM python:3.7-alpine

# Set metadata
LABEL Name=monvaccincovid Version=1.0.0 maintainer="Nicolas Candia <ncandia.pro@gmail.com>"

# Set workdir
WORKDIR /app

# Add all files to working directory
ADD . /app

# Install requirements
RUN set -ex \
    && apk --no-cache add --virtual build-dependencies \
        build-base \
        gcc \
        libc-dev \
        libffi-dev \
        python3-dev \
        mariadb-dev \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install -r requirements.txt

# Set application entrypoint
ENTRYPOINT ["python3"]

# Run application
CMD ["./app.py"]