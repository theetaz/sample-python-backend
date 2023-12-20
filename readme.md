### how to run the project

first intall the requirements using pip

```bash
pip3 install -r requirements.txt
```

configer the .env file based on the provided .env.example file

```bash
cp .env.example .env
```

run the project

```bash
python3 server.py
```

## how to run the migration

```bash
alembic revision --autogenerate -m "<your message>"
alembic upgrade head
```
