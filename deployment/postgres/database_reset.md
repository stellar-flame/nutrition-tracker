 System is in development so when schema changes occur easiest to reset the db.

 Local:
 ```
 python -m app.database.initialize.reset_db reset
 alembic revision --autogenerate -m "initial"
 alembic upgrade head
 ```

 AWS dev:
`initial` script should be in container
```
 python -m app.database.initialize.reset_db reset
 alembic upgrade head
 ```