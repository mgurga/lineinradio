FROM python:3-slim-bookworm

RUN apt-get -y update && apt-get install -y --no-install-recommends python3-django python3-pil python3-daphne python3-django-channels python3-django-q mpd mpc yt-dlp

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LIR_MEDIA="/media"
EXPOSE 8000

RUN ./setup.sh
CMD ./run.sh