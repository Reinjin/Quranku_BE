# Tahap 1: Base image untuk build dependencies (Python 3.10.0)
FROM python:3.10.0-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tentukan working directory
WORKDIR /app

# Install build dependencies seperti gcc, libffi-dev, dll.
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Salin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Install dependencies ke dalam folder temporer
RUN pip install --prefix=/install -r requirements.txt

# Tahap 2: Production image (Python 3.10.0)
FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tentukan working directory
WORKDIR /app

# Copy hanya dependencies dari tahap builder
COPY --from=builder /install /usr/local

# Salin semua file aplikasi ke dalam container
COPY . /app/

# Expose port yang digunakan oleh Flask
EXPOSE 5003

# Jalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "--access-logfile", "-", "-w", "4", "-b", "0.0.0.0:5003", "app:app"]