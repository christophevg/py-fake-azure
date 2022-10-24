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
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🏃‍♂️ Running Azure with:
📚 Function Apps
  📗 adding function app from services/hello_service
  🌎 Setting up fresh server for function app.
👀 creating function app from services/hello_service
  📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
  ✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
 * Serving Flask app 'azure.mock' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ⏰ tick
 ⏰ tick
```

Call it from the commandline:

```console
% curl "http://localhost:5000/api/hello/v1/?name=Christophe"
Hello, Christophe.
```

And see the functions in action...

```console
❤️  Function services.hello_service.hello_function received a request...
🗄  Created filename_a95af3ad-6705-4ec3-9c65-3a2d27cdb060.txt in local_blob_storage/container.
🔈 Notifying services.hello_service.hello2_function
127.0.0.1 - - [24/Oct/2022 09:05:36] "GET /api/hello/v1/?name=Christophe HTTP/1.1" 200 -
💕 Function services.hello_service.hello2_function was informed that someone said hello.
   👉 Christophe
```

## App Services

In `webapps/hello` a web application is hosted, serving a form that can target the function app...

```console
 % python -m azure serve_app_svc webapps/hello run
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🏃‍♂️ Running Azure with:
🌎 App Service from webapps/hello
  🌎 Loaded webapp webapps.hello.app
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
⏰ tick
⏰ tick
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
127.0.0.1 - - [24/Oct/2022 09:06:08] "GET / HTTP/1.1" 200 -
🍺 Pouring form.html.
127.0.0.1 - - [24/Oct/2022 09:06:10] "GET /form HTTP/1.1" 200 -
```

## All in one

You can run both at the same time ...

```console
% python -m azure serve_func_app services/hello_service serve_app_svc webapps/hello run
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🏃‍♂️ Running Azure with:
📚 Function Apps
  📗 adding function app from services/hello_service
🌎 App Service from webapps/hello
  🌎 Loaded webapp webapps.hello.app
👀 creating function app from services/hello_service
  📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
  ✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
⏰ tick
⏰ tick
```

And now visit [http://localhost:5000/form](http://localhost:5000/form) in a browser and try it...

And see them in action...

```console
🍺 Pouring form.html.
127.0.0.1 - - [24/Oct/2022 09:06:55] "GET /form HTTP/1.1" 200 -
🍺 Pouring jquery.min.js.
127.0.0.1 - - [24/Oct/2022 09:06:55] "GET /js/jquery.min.js HTTP/1.1" 304 -
127.0.0.1 - - [24/Oct/2022 09:06:59] "GET /api/hello/v1?name=Dave HTTP/1.1" 308 -
❤️  Function services.hello_service.hello_function received a request...
🗄  Created filename_b2a2f222-65b7-445e-96fd-f5fef7fe0937.txt in local_blob_storage/container.
🔈 Notifying services.hello_service.hello2_function
127.0.0.1 - - [24/Oct/2022 09:06:59] "GET /api/hello/v1/?name=Dave HTTP/1.1" 200 -
💕 Function services.hello_service.hello2_function was informed that someone said hello.
   👉 Dave
```

### Gunicorn

You can also run from gunicorn: Set up environment variables pointing to your function app and/or app service and fire up gunicorn...

```console
% FUNC_APP=services/hello_service APP_SVC=webapps/hello gunicorn -b 0.0.0.0:5000 azure.app:server
[2022-10-24 09:07:19 +0200] [91273] [INFO] Starting gunicorn 20.1.0
[2022-10-24 09:07:19 +0200] [91273] [INFO] Listening at: http://0.0.0.0:5000 (91273)
[2022-10-24 09:07:19 +0200] [91273] [INFO] Using worker: sync
[2022-10-24 09:07:19 +0200] [91287] [INFO] Booting worker with pid: 91287
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🏃‍♂️ Running Azure with:
📚 Function Apps
  📗 adding function app from services/hello_service
🌎 App Service from webapps/hello
  🌎 Loaded webapp webapps.hello.app
👀 creating function app from services/hello_service
  📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
  ✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
🔐 OAuth fake token endpoint ready @ /oauth/token
⏰ tick
⏰ tick
```

## Multiple Function Apps ... ⏰ tick

In the `services/` folder another "service" is availabe: `file_service`. It contains two other functions. You can load multiple function apps/services at the same time:

```console
% python -m azure serve_func_app services/hello_service serve_func_app services/file_service serve_app_svc webapps/hello run
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
⏰ tick
🏃‍♂️ Running Azure with:
📚 Function Apps
  📗 adding function app from services/hello_service
  📗 adding function app from services/file_service
🌎 App Service from webapps/hello
  🌎 Loaded webapp webapps.hello.app
👀 creating function app from services/hello_service
  📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
  ✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
👀 creating function app from services/file_service
  ⏰ scheduling services.file_service.timed_check_function every 5 seconds...
  📍 Setting up API endpoint for services.file_service.create_file_function on create
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
⏰ tick
⏰ tick
⏰ tick
⏰ tick
⏰ tick
🔎 looking in todo for tts <= 1666595497
⏰ tick
⏰ tick
```

```console
% FUNC_APP="services/hello_service services/file_service" APP_SVC=webapps/hello gunicorn -b 0.0.0.0:5000 azure.app:server
[2022-10-24 09:09:56 +0200] [93312] [INFO] Starting gunicorn 20.1.0
[2022-10-24 09:09:56 +0200] [93312] [INFO] Listening at: http://0.0.0.0:5000 (93312)
[2022-10-24 09:09:56 +0200] [93312] [INFO] Using worker: sync
[2022-10-24 09:09:56 +0200] [93326] [INFO] Booting worker with pid: 93326
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
⏰ tick
🏃‍♂️ Running Azure with:
📚 Function Apps
  📗 adding function app from services/hello_service
  📗 adding function app from services/file_service
🌎 App Service from webapps/hello
  🌎 Loaded webapp webapps.hello.app
👀 creating function app from services/hello_service
  📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
  ✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
👀 creating function app from services/file_service
  ⏰ scheduling services.file_service.timed_check_function every 5 seconds...
  📍 Setting up API endpoint for services.file_service.create_file_function on create
🔐 OAuth fake token endpoint ready @ /oauth/token
⏰ tick
⏰ tick
⏰ tick
⏰ tick
⏰ tick
🔎 looking in todo for tts <= 1666595401
⏰ tick
⏰ tick
```

Now, we've added the `file_service` it's time to explain the "⏰ tick" debug statements: Every second py-fake-azure checks if any scheduled functions, aka timer triggered functions, are to be run. And the `file_service` has such a function: `timed_check_function`, which is to be run every 5 seconds.

After 5 ticks, we see it in action, looking for blobs in the todo container with a tag tts <= the current time in epoch format.

You can play with this "service", by creating new files with `curl "http://localhost:5000/api/create?filename=afile.txt&content=something"` and see what the timed function does...

> Pro-Tip: add a `LOG_LEVEL=INFO` env variable to reduce the logging to a more functional level 

```console
⚠️ No queue for todo
📄 created blob with a tts in 10s
🔔 afile.txt is due ({'tts': '1666596158'}
  ☝️ first attempt
🔔 afile.txt is due ({'tts': '1666596165', 'retries': '0'}
  ✌️ retrying for 1 time @ 1666596180
🔔 afile.txt is due ({'tts': '1666596180', 'retries': '1'}
  ✌️ retrying for 2 time @ 1666596200
🔔 afile.txt is due ({'tts': '1666596200', 'retries': '2'}
  🛑 3 retries, we're done.

```

`create_file_function` just creates a file with the filename and content provided and gives it a time to send (tts), which is basically an epoch timestamp in the future.

`timed_check_function` is a timer triggered function that executes every 5 seconds, checks for files with a tts lower than the current epoch time, and if found, does nothing and reshedules it up to 3 times.

You can now apply an exponential back off procedure you need ;-)
