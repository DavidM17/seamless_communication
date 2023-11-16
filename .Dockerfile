FROM python:3.9.6

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN wget -q https://huggingface.co/facebook/seamless-m4t-unity-small/resolve/main/unity_on_device.ptl

RUN mkdir -p /app/audios && mkdir -p /app/output && pip install -r requirements.txt

CMD [ "python", "app.py" ]