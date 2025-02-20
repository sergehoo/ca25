FROM python:3.9-slim
LABEL authors="ogahserge"

WORKDIR /siade25-app
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install system dependencies, including those necessary for building wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    gcc \
    python3-distutils \
    python3-setuptools \
    python3-dev \
    libgl1-mesa-glx \  # 🔥 Ajout de la librairie pour OpenCV
    libglib2.0-0 \  # 🔥 Ajout d'une dépendance pour éviter d'autres erreurs
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

RUN pip install --upgrade pip

COPY requirements.txt /siade25-app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /siade25-app/

RUN apt-get update && apt-get install -y postgresql-client
EXPOSE 8000

CMD ["gunicorn", "siade25.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4", "--timeout=180", "--log-level=debug"]