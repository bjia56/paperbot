FROM python:3.12-slim

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt_tab')"

CMD ["python", "app.py"]