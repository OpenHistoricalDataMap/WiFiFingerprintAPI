FROM python:3.6
MAINTAINER Tom Morelly "tom-morelly@gmx.de"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]


