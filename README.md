# Stores REST API
This is an example of a REST API for creating and interacting with a relational 
database of items/products and stores.

### Build & deploy

This repository has a Dockerfile for building a docker image. By executing ```docker_build.sh```, a docker image will be created.
The deploy can be made by using the docker-compose.yml file and a `.env` file (use `.env.example` as a reference). The database is created when
running the app if it doesn't exists previously.

### API documentation.
You can access to the swagger documentation with the URL `/swagger-ui`

### Postman
Inside the `postman/` folder you can find a Postman collection and environment variables,
which can be imported if you will use Postman for interacting with the app.

### Creating a user and logging
With the endpoint `/register` you can create a user with your username and password, and it will be stored in the database.

The `/loggin` endpoint is used for authentication. By introducing your username and password, it will return a JWT token that you will need
in order to interact with some endpoints (for example `POST /item`). 
The token is introduced in a header: `Authentication: Bearer {{token}}` 
(you can save it in the `{{token}}` environment variable in Postman, 
and it will be used by the endpoints in the Postman collection previously mentioned.)

### Admin privilege
There are some endpoints that require admin privilege (for example `DELETE /item/{item_id}`). 
By default, the first registered user (user id = 1) will be the admin and only the admin user can interact with these special endpoints.