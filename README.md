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
🔈 loaded blob tags
🔈 Started Storage Account notifier thread.
🌎 Setting up server for function app.
⏰ scheduling services.hello_service.timed_check_function every 5 seconds...
📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
📍 Setting up API endpoint for services.hello_service.create_file_function on create
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
❤️  Function services.hello_service.hello_function received a request...
🗄  Created filename_0154a84e-3af4-4459-a874-fc32f915c6a4.txt in local_blob_storage/container.
🔈 Notifying services.hello_service.hello2_function
127.0.0.1 - - [23/Oct/2022 16:08:47] "GET /api/hello/v1/?name=Christophe HTTP/1.1" 200 -
💕 Function services.hello_service.hello2_function was informed that someone said hello.
   👉 Christophe
```

## App Services

In `webapps/hello` a web application is hosted, serving a form that can target the function app...

```console
 % python -m azure serve_app_svc webapps/hello run
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🔈 loaded blob tags
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
127.0.0.1 - - [23/Oct/2022 16:07:21] "GET / HTTP/1.1" 200 -
🍺 Pouring form.html.
127.0.0.1 - - [23/Oct/2022 16:07:21] "GET /form HTTP/1.1" 304 -
```

## All in one

You can run both at the same time ...

```console
% python -m azure serve_func_app services/hello_service serve_app_svc webapps/hello run
🗄  Constructing a fake Storage Account in local_blob_storage.
🔈 Notifying changes to container via inbox
🔈 loaded blob tags
🔈 Started Storage Account notifier thread.
🌎 Loaded webapp webapps.hello.app
⏰ scheduling services.hello_service.timed_check_function every 5 seconds...
📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
✋ subscribing services.hello_service.hello2_function as handler for inbox
🗄  Set up subscription on inbox for services.hello_service.hello2_function.
📍 Setting up API endpoint for services.hello_service.create_file_function on create
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
127.0.0.1 - - [23/Oct/2022 16:06:15] "GET /form HTTP/1.1" 200 -
🍺 Pouring jquery.min.js.
127.0.0.1 - - [23/Oct/2022 16:06:15] "GET /js/jquery.min.js HTTP/1.1" 200 -
127.0.0.1 - - [23/Oct/2022 16:06:15] "GET /apple-touch-icon-precomposed.png HTTP/1.1" 404 -
127.0.0.1 - - [23/Oct/2022 16:06:15] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [23/Oct/2022 16:06:15] "GET /apple-touch-icon.png HTTP/1.1" 404 -
127.0.0.1 - - [23/Oct/2022 16:06:25] "GET /api/hello/v1?name=Dave HTTP/1.1" 308 -
❤️  Function services.hello_service.hello_function received a request...
🗄  Created filename_c0261a74-e8f8-4459-9647-821241ae042a.txt in local_blob_storage/container.
🔈 Notifying services.hello_service.hello2_function
127.0.0.1 - - [23/Oct/2022 16:06:25] "GET /api/hello/v1/?name=Dave HTTP/1.1" 200 -
💕 Function services.hello_service.hello2_function was informed that someone said hello.
   👉 Dave
```

### Gunicorn

You can also run from gunicorn: Set up environment variables pointing to your function app and/or app service and fire up gunicorn...

```console
% LOG_LEVEL=INFO FUNC_APP=services/hello_service APP_SVC=webapps/hello gunicorn -b 0.0.0.0:5000 azure.app:server
[2022-10-23 16:03:04 +0200] [99865] [INFO] Starting gunicorn 20.1.0
[2022-10-23 16:03:04 +0200] [99865] [INFO] Listening at: http://0.0.0.0:5000 (99865)
[2022-10-23 16:03:04 +0200] [99865] [INFO] Using worker: sync
[2022-10-23 16:03:04 +0200] [99879] [INFO] Booting worker with pid: 99879
🏃‍♂️ Running Azure with:
📚 Function Apps
  📗 adding function app from services/hello_service
🌎 App Service from webapps/hello
⏰ scheduling services.hello_service.timed_check_function every 5 seconds...
📍 Setting up API endpoint for services.hello_service.hello_function on hello/v1/
✋ subscribing services.hello_service.hello2_function as handler for inbox
📍 Setting up API endpoint for services.hello_service.create_file_function on create
```

Now, try a couple of other functions: `create_file_function` and `timed_check_function`.

Kick them off with a `curl "http://localhost:5000/api/create?filename=new2&content=new2"` command...

```console
⚠️ No queue for todo
📄 created blob with a tts in 10s
🔔 new2 is due ({'tts': '1666533816'}
  ☝️ first attempt
🔔 new2 is due ({'tts': '1666533825', 'retries': '0'}
  ✌️ retrying for 1 time @ 1666533840
🔔 new2 is due ({'tts': '1666533840', 'retries': '1'}
  ✌️ retrying for 2 time @ 1666533860
🔔 new2 is due ({'tts': '1666533860', 'retries': '2'}
  🛑 3 retries, we're done.
```

`create_file_function` just creates a file with the filename and content provided and gives it a time to send (tts), which is basically an epoch timestamp in the future.

`timed_check_function` is a timer triggered function that executes every 5 seconds, checks for files with a tts lower than the current epoch time, and if found, does nothing and reshedules it up to 3 times.

You can now apply an exponential back off procedure you need ;-)
