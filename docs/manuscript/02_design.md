# Design

The core layer defines typed content, user, assessment, metadata and
analytics objects. Domain services create and update these objects
and own transient storage for local use. A content record has a UUID,
a parent when it belongs to a hierarchy, an author, a declared format,
and a status. The assessment and analytics services coordinate around
the same identifier type.

A FastAPI request adapter exposes the domain services over HTTP.
The application assembles content, user, assessment and analytics
routers. FastAPI supplies the OpenAPI schema and interactive
documentation [@fastapi]. The development web application uses
per-process service state. Database adapters provide a separate
asynchronous persistence interface available to integrating callers.

A documentation generator analyzes the source tree using Python's
abstract syntax tree [@python_ast]. It builds a module index and
extracts package, class and method descriptions. It can produce
these inventories without requiring a model provider or application
database.
