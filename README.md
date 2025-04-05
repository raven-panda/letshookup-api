# Let's Hook Up !
## Group chats for work teams or friends group

## Technical Specs

- Language used : [Python](https://www.python.org/) for backend, [JavaScript](https://developer.mozilla.org/fr/docs/Web/JavaScript)
- Frameworks used : [Flask](https://flask.palletsprojects.com/en/stable/), [React](https://react.dev/)
- Database : [PostgreSQL](https://www.postgresql.org/)

## Start docker container (or change DATABASE_URL in env to use your local one and skip this step)

```sh
cd ./Backend
docker compose up
```

## Init and start Flask project

On linux :

```sh
cd ./Backend

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt # or use 'python -m pip' if you don't have it installed globally
python run.py
```

On windows :

```powershell
cd ./Backend

py -m venv .venv
source .venv\Scripts\activate
pip install -r requirements.txt # or use 'py -m pip' if you don't have it installed globally
py run.py
```
