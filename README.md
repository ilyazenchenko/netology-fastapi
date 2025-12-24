## Запуск через Docker

docker volume create todo_data
docker volume create shorturl_data

docker run -d -p 8000:80 -v todo_data:/app/data <login>/todo-service
docker run -d -p 8001:80 -v shorturl_data:/app/data <login>/shorturl-service

## Swagger
http://localhost:8000/docs  
http://localhost:8001/docs
