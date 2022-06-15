# Local Mocked Azure Support

> A Saturday night evening of fun resulted in a very minimalistic, but fully controlable fake Azure environment in Python with support for function apps, service apps, blob storage and service bus events.

## Minimal Survival Commands

```console
$ pip install -r requirements.txt
```

## Function Apps

In `services/hello_service` two functions are defined: `hello_function` and `hello2_function`. The former has an HttpTrigger and creates a file in blob storage using an output blob binding. The latter receives an event via a Service Bus message and fetches the file created by the first function.

```console
% python -m azure serve_func_app services/hello_service run
🗄 Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🔈 Started Storage Account notifier thread.
🌎 Setting up server for function app.
📍 Setting up API endpoint for hello_function on hello/v1/
🗄 Set up subscription on inbox for hello2_function.
 * Serving Flask app 'azure.mock' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Call it from the commandline:

```console
% curl "http://localhost:5000/api/hello/v1/?name=Christophe"
Hello, Christophe.
```

And see the functions in action...

```console
❤️ Function services.hello_service.hello_function received a request...
🗄 Created filename_51b7183b-4916-49bf-9b84-807ac3332606.txt in local_blob_storage/container.
🔈 Notifying hello2_function
127.0.0.1 - - [15/Jun/2022 23:10:43] "GET /api/hello/v1/?name=Christophe HTTP/1.1" 200 -
💕 Function services.hello_service.hello2_function was informed that someone said hello.
   👉 Christophe
```

## App Services

In `webapps/hello` a web application is hosted, serving a form that can target the function app...

```console
% python -m azure serve_app_svc webapps/hello run
🗄 Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🔈 Started Storage Account notifier thread.
🌎 Loaded webapp webapps.hello.app
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Try getting some 

```console
% curl "http://localhost:5000/"    
Hello, World!

% curl "http://localhost:5000/form"
<html>
<body>
  api : <input id="api" value="http://localhost:5000/api/hello/v1" size="25"><br>
  name : <input id="name" value="Dave"><br>
  <button onclick="get();">get</button><br>
  <div id="response"></div>
</body>
<script src="/js/jquery.min.js"></script>
<script>
  function get() {
    var url = $("#api").val() + "?name=" + $("#name").val();
    $.get(url, function(result) {
      $("#response").html(result);
    });
  }
</script>
</html>
```

Ans see the web app in action:

```console
🍺 Pouring a greeting.
127.0.0.1 - - [15/Jun/2022 23:15:55] "GET / HTTP/1.1" 200 -
🍺 Pouring form.html.
127.0.0.1 - - [15/Jun/2022 23:16:12] "GET /form HTTP/1.1" 200 -
```

## All in one

You can run both at the same time ...

```console
% python -m azure serve_func_app services/hello_service serve_app_svc webapps/hello run
🗄 Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🔈 Started Storage Account notifier thread.
🌎 Loaded webapp webapps.hello.app
📍 Setting up API endpoint for hello_function on hello/v1/
🗄 Set up subscription on inbox for hello2_function.
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

And now visit [http://localhost:5000/form](http://localhost:5000/form) in a browser and try it...

And see them in action...

```console
🍺 Pouring form.html.
127.0.0.1 - - [15/Jun/2022 23:17:07] "GET /form HTTP/1.1" 304 -
🍺 Pouring jquery.min.js.
127.0.0.1 - - [15/Jun/2022 23:17:07] "GET /js/jquery.min.js HTTP/1.1" 304 -
127.0.0.1 - - [15/Jun/2022 23:17:10] "GET /api/hello/v1?name=Dave HTTP/1.1" 308 -
❤️  Function services.hello_service.hello_function received a request...
🗄  Created filename_ed80bc6d-ba52-41e3-ac90-3cce857c55bc.txt in local_blob_storage/container.
🔈 Notifying hello2_function
127.0.0.1 - - [15/Jun/2022 23:17:10] "GET /api/hello/v1/?name=Dave HTTP/1.1" 200 -
💕 Function services.hello_service.hello2_function was informed that someone said hello.
   👉 Dave
```

### Gunicorn

You can also run from gunicorn: Set up environment variables pointing to your function app and/or app service and fire up gunicorn...

```console
% export FUNC_APP=services/hello_service 
% export APP_SVC=webapps/hello           
% gunicorn -b 0.0.0.0:5000 azure.app:server
[2022-06-15 23:18:28 +0200] [80208] [INFO] Starting gunicorn 20.1.0
[2022-06-15 23:18:28 +0200] [80208] [INFO] Listening at: http://0.0.0.0:5000 (80208)
[2022-06-15 23:18:28 +0200] [80208] [INFO] Using worker: sync
[2022-06-15 23:18:28 +0200] [80225] [INFO] Booting worker with pid: 80225
🏃‍♂️ Running Azure from services/hello_service + webapps/hello
🗄 Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🔈 Started Storage Account notifier thread.
🌎 Loaded webapp webapps.hello.app
📍 Setting up API endpoint for hello_function on hello/v1/
🗄 Set up subscription on inbox for hello2_function.
🔐 OAuth fake token endpoint ready @ /oauth/token
```
