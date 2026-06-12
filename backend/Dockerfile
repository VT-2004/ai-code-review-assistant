FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . .

# expose port
EXPOSE 8000

# start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]