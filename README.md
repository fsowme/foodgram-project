fsow.cf

[![foodgram workflow](https://github.com/fsowme/foodgram-project/actions/workflows/foodgram_workflow.yaml/badge.svg?event=push)](https://github.com/fsowme/foodgram-project/actions/workflows/foodgram_workflow.yaml)


# Foodgram

Final training project.  Ready to up in Docker.

## Getting Started

These instructions will get you a copy of the project up and running in docker container for development and testing purposes. 

### Prerequisites

Docker and docker-compose must be installed in your system. More information you can take on official site of Docker.

[docker](https://docs.docker.com/engine/install/)

[docker-compose](https://docs.docker.com/compose/install/)


### Installing

Clone this project and go to new folder:

```
git clone git@github.com:fsowme/foodgram-project.git
cd foodgram-project/foodgram/

```

Create .env file with parameters for connecting to the base:

```
touch .env
nano .env
```
.env example:

```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

```
Save and exit from .env file and run command to create docker containers. After this one you will have three containers, one of them with postgresql database, one with web project and one with nginx server.
```
docker-compose up -d

```
After creating enter the container with web project (show running containers: sudo docker-compose ps). Update packages and pip, make migrations and superuser
```
docker exec -it <container_name> bash
apt-get update && apt-get upgrade -y
python -m pip install --upgrade pip
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

```

And now you can start browser and open start page http://localhost with admin page http://localhost/admin/

## Built With

* [Django](https://www.djangoproject.com/) - The web framework used
* [Django REST framework](https://www.django-rest-framework.org/) - API framework


## Authors

***Vitalii Mikhailov**