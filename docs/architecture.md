# Architecture

The project separates HTTP request adapters, service operations and typed
domain models. Applications can use the service classes directly.

1. `curriculum.routes` assembles the FastAPI application and the content,
   user, assessment and analytics routers.
2. Service packages apply domain operations such as creating a content
   record, changing a lifecycle state, grading an assessment and
   recording a learning event.
3. `curriculum.core` defines validated records, metadata, identifiers and
   enums. Dublin Core and LRMI-inspired metadata fields are represented
   as typed models.
4. `curriculum.db` defines an asynchronous database interface and offers
   PostgreSQL and MongoDB adapters for callers that explicitly wire them
   into their workflows.

The default route services hold state in their process. Restarting the
development server discards that state. Redis, search adapters, external
analytics, and model services each require separate configuration when
used. The `/health` response confirms the web process responds.

Rendering, content generation, teaching, accessibility, communication,
mobile workflows and integration adapters each have their own services.
Consult the [module reference](reference/modules/index.md) for the
concrete entry points. The [verification guide](development/testing.md)
describes the executable scope of the checked-in test and documentation
fixtures.
