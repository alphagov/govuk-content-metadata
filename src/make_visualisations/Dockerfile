FROM python:3.9-slim

EXPOSE 8080

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN python download_models.py

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
