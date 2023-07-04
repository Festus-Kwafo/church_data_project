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
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm


COPY src/package*.json ./
RUN npm install

# Copy project
COPY . /church_data_project/

#run webpack
COPY src/webpack.common.js /church_data_project/src/
COPY src/webpack.prod.js /church_data_project/src/

RUN npm run build

RUN python manage.py collectstatic --noinput --clear
RUN python manage.py makemigrations
RUN python manage.py migrate
EXPOSE 8000


