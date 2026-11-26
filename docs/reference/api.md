# API reference

Follow the [quickstart](../quickstart.md) to run the local FastAPI
application. Its `/docs` and `/redoc` pages derive from the same
`/openapi.json` document as client generators. Use that schema for
operation parameters, bodies and response types.

| Route group | Responsibility |
| --- | --- |
| `/health` | Application process status and version. |
| `/api/v1/content` | Content records, listing, status, hierarchy and rendering. |
| `/api/v1/users` | User records, roles, login and token refresh. |
| `/api/v1/assessments` | Assessment definitions, questions, attempts and results. |
| `/api/v1/analytics` | Learning events, sessions and aggregate views. |

The checkout's default configuration is for local development. Route
contracts and service permissions are tracked in the application source
and its tests. API availability alone provides no guarantee of durable
storage or deployment readiness.

See [architecture](../architecture.md) for where each route's state
lives and the [library walkthrough](../library.md) for a server-free
example.
