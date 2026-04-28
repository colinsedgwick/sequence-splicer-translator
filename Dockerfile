FROM python:3.12

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY sequence_processor.py /code/sequence_processor.py
COPY app.py /code/app.py
WORKDIR /code

RUN chmod ugo+x /code/sequence_processor.py
ENV PATH="/code:$PATH"