FROM python:3.12

RUN pip3 install biopython

COPY sequence_processor.py /code/sequence_processor.py

RUN chmod ugo+x /code/sequence_processor.py

ENV PATH="/code:$PATH"