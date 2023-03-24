#Pull base image
FROM python:3.9

#set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Install django dependencies
RUN pip install --upgrade pip
COPY requirements.txt /church_data_project/
RUN pip install -r /church_data_project/requirements.txt

#work directory
WORKDIR /church_data_project/src

#install npm dependencies 
RUN apt-get update && apt-get upgrade -y && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
apt-get install -y nodejs



COPY src/package*.json ./
RUN npm install

# Copy project
COPY . /church_data_project/

ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
RUN echo ${POSTGRES_DB}
RUN echo ${POSTGRES_USER}
RUN echo ${POSTGRES_PASSWORD}

#run webpack
COPY src/webpack.common.js /church_data_project/src/
COPY src/webpack.prod.js /church_data_project/src/

RUN npm run build

RUN python manage.py collectstatic --noinput
EXPOSE 80


