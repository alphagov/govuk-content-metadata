FROM python:3.9-slim

EXPOSE 8501

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN ls --recursive .

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
