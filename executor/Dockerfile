FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./executor.py" ]

# entrypoint tail
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]