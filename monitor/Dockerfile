FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "-u", "./monitor.py" ]

# entrypoint tail
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]