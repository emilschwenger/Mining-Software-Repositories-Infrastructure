FROM python:latest
WORKDIR /usr/app/src
COPY ./tool/ ./tool/
COPY requirements.txt ./
COPY config.json ./
COPY repository_list.txt ./
RUN apt-get install libmagic1
RUN pip install -r requirements.txt
CMD ["chmod", "777", "/repo_share"]
CMD ["mkdir", "-p", "/repo_clone"]
CMD ["python", "tool/main.py"]