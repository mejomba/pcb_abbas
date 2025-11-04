# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# پورت 8000 را برای Gunicorn باز کن
EXPOSE 8000

# (اختیاری ولی پیشنهادی) یک اسکریپت entrypoint برای اجرای migrate ها بسازید
# CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]
# برای توسعه، می‌توانید از runserver استفاده کنید:
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]