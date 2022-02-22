# starnavi-testing
## Configuration
### config.ini
#### web
debug = debug value for fastapi, 1 - True, 0 - False  
sa_echo = sqlalchemy engine echo value, 1 - True, 0 - False  
access_token_expire_seconds = user authorization jwt token expiration time in seconds  
jwt_algorithm = user authorization jwt algorithm, HS256 suggested  
jwt_secret_key = user authorization jwt secret key, generate using `openssl rand -hex 32`  
#### db
sa_url = sqlalchemy url to connect to db, use aiomysql  
alembic_sa_url = sqlalchemy url to connect to db, use pymsql  
test_sa_url = sqlalchemy url to connect to db while tests, use aiomysql  
#### bot
number_of_users = number of users to create  
max_posts_per_user = max posts created by one user  
max_likes_per_user = max likes made by one user  
base_url = base url for bot to connect to a running instance of web app  
### .env
values from .env are used in docker-compose  
MYSQL_PORT=mysql port  
MYSQL_ROOT_PASSWORD=mysql root password  
MYSQL_USER=mysql user username  
MYSQL_PASSWORD=mysql user password  
MYSQL_DATABASE=mysql database name  
NGINX_PORT=nginx port  
## Installation and launch
1. clone repo `git clone https://github.com/drforse/starnavi-testing`  
2. enter repo directory `cd starnavi-testing`  
3. create config file `cp config.ini.template config.ini`  
4. create .env file `cp .env.template .env`  
5. fill in config.ini and .env according to section *Configuration*
6. run docker containers `docker-compose up -d`  
## bot
`python bot.py` to run random users/posts/likes creation  
`python bot.py --clear` to clear all randomly created users/posts/likes  
`python bot.py --help` to check help on bot  
## tests
to run tests you need to have mysql installed and launched and test_sa_url set in config.ini  
1. make sure you are in the root project directory  
2. create environment and install packages `poetry install`  
3. run tests `pytest`  