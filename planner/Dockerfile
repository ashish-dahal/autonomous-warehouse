FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# add mosquitto client
RUN apk add --no-cache mosquitto-clients

COPY . .

EXPOSE 8080

CMD [ "python", "-u", "./planner.py" ]

# entrypoint tail
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]