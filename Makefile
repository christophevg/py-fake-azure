LOG_LEVEL=INFO
FUNC_APP="services/hello_service services/file_service"
APP_SVC=webapps/hello

all: clean
	LOG_LEVEL=${LOG_LEVEL} FUNC_APP=${FUNC_APP} APP_SVC=${APP_SVC} gunicorn -b 0.0.0.0:5000 azure.app:server

clean:
	rm -rf local_blob_storage
