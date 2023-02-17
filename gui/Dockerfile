FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY . .

# python -m http.server 8080 --bind 127.0.0.1 --directory /path/to/dir
CMD [ "python", "-m", "http.server", "8080" ]

# entrypoint tail
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]