# Ground truth Q&A pairs for Flask repo (pallets/flask)
EVAL_DATASET = [
    {
        "question": "How does Flask handle URL routing?",
        "ground_truth": "Flask uses a URL map and decorators like @app.route() to register view functions to URL patterns. Internally it uses Werkzeug's routing system."
    },
    {
        "question": "What is the application context in Flask?",
        "ground_truth": "The application context pushes a copy of the application object so extensions and code can access it without passing the app around. It is managed via current_app and g proxies."
    },
    {
        "question": "How does Flask manage request context?",
        "ground_truth": "Flask pushes a request context for each incoming request containing the request and session proxy objects. It is pushed at the start of the request and popped after the response."
    },
    {
        "question": "What is the purpose of the g object in Flask?",
        "ground_truth": "g is a namespace object on the application context used to store data during a request. It is reset after each request and is used to store things like database connections."
    },
    {
        "question": "How does Flask handle blueprints?",
        "ground_truth": "Blueprints allow splitting an application into reusable components. They record operations to be executed when registered on an application using app.register_blueprint()."
    },
    {
        "question": "How does Flask's template rendering work?",
        "ground_truth": "Flask uses Jinja2 as its template engine. render_template() loads templates from the templates folder and renders them with provided context variables."
    },
    {
        "question": "What happens when a Flask app starts up?",
        "ground_truth": "Flask runs WSGI callable which creates the app context, pushes request context, dispatches request to the matched URL rule and view function, then returns response."
    },
    {
        "question": "How does Flask handle errors and exceptions?",
        "ground_truth": "Flask uses errorhandler decorators to register functions for specific HTTP error codes or exception types. Unhandled exceptions return 500 responses."
    },
    {
        "question": "What is the Flask application factory pattern?",
        "ground_truth": "The factory pattern creates the Flask app inside a function, allowing multiple instances with different configs. create_app() function initializes extensions and blueprints."
    },
    {
        "question": "How does Flask handle static files?",
        "ground_truth": "Flask serves static files from the static folder via the /static URL prefix. url_for('static', filename='...') generates URLs for static assets."
    },
    {
        "question": "How does session management work in Flask?",
        "ground_truth": "Flask uses signed cookies for client-side sessions using the SECRET_KEY. The session object is a dict-like object that serializes to a secure cookie."
    },
    {
        "question": "What is before_request in Flask?",
        "ground_truth": "before_request registers functions to run before each request. If it returns a value, the view function is skipped and that value is used as the response."
    },
    {
        "question": "How does Flask's test client work?",
        "ground_truth": "Flask provides a test client via app.test_client() that simulates HTTP requests without running a server. It is used for unit testing views and routes."
    },
    {
        "question": "What is the purpose of Flask's config object?",
        "ground_truth": "Flask's config object is a dict subclass that stores configuration variables like DEBUG, SECRET_KEY. It can be loaded from objects, files, or environment variables."
    },
    {
        "question": "How does Flask signal system work?",
        "ground_truth": "Flask uses Blinker library for signals like request_started and request_finished. Signals allow decoupled components to get notified when actions occur."
    },
]
