FROM python:3.11.1

WORKDIR /bot

COPY requirements.txt /bot/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /bot/

ENTRYPOINT ["python", "bot.py"]
