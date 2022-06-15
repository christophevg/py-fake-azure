# Local Mocked Azure Support

> A Saturday night evening of fun resulted in a very minimalistic, but fully controlable fake Azure environment in Python with support for function apps, service apps, blob storage and service bus events.

## Minimal Survival Commands

```bash
$ pip install -r requirements.txt
```

## Function Apps

```bash
% python -m azure serve_func_app services/hello_service run
[2022-06-15 14:08:59 +0200] [WARNING] [azure.storage.blob] no storage queues defined
[2022-06-15 14:08:59 +0200] [INFO] [azure.storage.blob] started SA notifier...
[2022-06-15 14:08:59 +0200] [INFO] [__main__] setting up API server
[2022-06-15 14:08:59 +0200] [INFO] [azure.func_app] setting up API for hello_function on hello/v1/
 * Serving Flask app '__main__' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
[2022-06-15 14:08:59 +0200] [INFO] [werkzeug]  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
[2022-06-15 14:09:01 +0200] [INFO] [services.hello_service.hello_function] version: 1.0.0 / name: Christophe
[2022-06-15 14:09:01 +0200] [INFO] [werkzeug] 127.0.0.1 - - [15/Jun/2022 14:09:01] "GET /api/hello/v1/?name=Christophe HTTP/1.1" 200 -

```

Call it from the commandline:

```bash
% curl "http://localhost:5000/api/hello/v1/?name=Christophe"
Hello, Christophe.
```

## App Services

```bash
% python -m azure serve_app_svc webapps/hello run
[2022-06-15 14:13:34 +0200] [WARNING] [azure.storage.blob] no storage queues defined
[2022-06-15 14:13:34 +0200] [INFO] [azure.storage.blob] started SA notifier...
[2022-06-15 14:13:34 +0200] [INFO] [azure.app_svc] loaded webapp webapps.hello.app
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
[2022-06-15 14:13:34 +0200] [INFO] [werkzeug]  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Try it:

```bash
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

## All in one

```bash
% python -m azure serve_func_app services/hello_service serve_app_svc webapps/hello run
[2022-06-15 14:14:38 +0200] [WARNING] [azure.storage.blob] no storage queues defined
[2022-06-15 14:14:38 +0200] [INFO] [azure.storage.blob] started SA notifier...
[2022-06-15 14:14:38 +0200] [INFO] [azure.app_svc] loaded webapp webapps.hello.app
[2022-06-15 14:14:38 +0200] [INFO] [azure.func_app] setting up API for hello_function on hello/v1/
 * Serving Flask app 'webapps.hello.app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
[2022-06-15 14:14:38 +0200] [INFO] [werkzeug]  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

And now visit [http://localhost:5000/form](http://localhost:5000/form) in a browser and try it...

