# To setup locally

0. Install sqlite3
```
$ sudo apt install sqlite3  // or whatever your package manager is
```

1. Create python3 virtual environment

```
$ python3 -m venv venv && source venv/bin/activate
```

2. Install dependencies
```
$ pip install -r requirements.txt
```

3. Setup DB
First you you'll need to comment out this block from the bottom of app/models.py (I know, I'm so sorry...)
```
if len(Account.query.all()) == 0:
    a = Account(
        description="Party account",
        platinum=0,
        gold=0,
        electrum=0,
        silver=0,
        copper=0,
    )
    db.session.add(a)
    db.session.commit()
```
Then create the database
```
$ flask db upgrade
```
Uncomment the block from models.py

4. Run the app
```
$ flask run
```