FROM python:2-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Kick off deployment script that creates DB if not existing
CMD [ "sh", "runProd.sh" ]
