all:
	FUNC_APP=services/hello_service APP_SVC=webapps/hello gunicorn -b 0.0.0.0:5000 azure.app:server
