# python base
FROM python:3.9

# set workdir
WORKDIR /code

# copy requirements
COPY ./requirements.txt /code/requirements.txt

# install requirements
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN python -m spacy download en_core_web_sm

# copy all
COPY ./app /code/app

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
