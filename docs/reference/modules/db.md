# Database adapters

Wire a `DatabaseInterface` explicitly when a workflow needs persistence. `DatabaseManager` registers a `MongoDBAdapter` or `PostgreSQLAdapter`; start and stop the configured adapters through their asynchronous lifecycle. The default web development setup uses in-process stores.

[Source package](https://github.com/docxology/course/tree/main/src/curriculum/db)
