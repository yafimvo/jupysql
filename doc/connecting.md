---
jupytext:
  notebook_metadata_filter: myst
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
myst:
  html_meta:
    description lang=en: "Connect to a SQL database from a Jupyter notebook"
    keywords: "jupyter, sql, jupysql"
    property=og:locale: "en_US"
---

# Connecting

Connection strings are [SQLAlchemy URL](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls) standard.

Some example connection strings:

```
mysql+pymysql://scott:tiger@localhost/foo
oracle://scott:tiger@127.0.0.1:1521/sidname
sqlite://
sqlite:///foo.db
mssql+pyodbc://username:password@host/database?driver=SQL+Server+Native+Client+11.0
```

Note that `mysql` and `mysql+pymysql` connections (and perhaps others)
don't read your client character set information from .my.cnf.  You need
to specify it in the connection string::

```
mysql+pymysql://scott:tiger@localhost/foo?charset=utf8
```

Note that an `impala` connection with [`impyla`](https://github.com/cloudera/impyla) for HiveServer2 requires disabling autocommit::

```
%config SqlMagic.autocommit=False
%sql impala://hserverhost:port/default?kerberos_service_name=hive&auth_mechanism=GSSAPI
```

Additionally, note that autocommit features for `pytds` connections are disabled.

Connection arguments not whitelisted by SQLALchemy can be provided as
a flag with (-a|--connection_arguments)the connection string as a JSON string. See [SQLAlchemy Args](https://docs.sqlalchemy.org/en/13/core/engines.html#custom-dbapi-args)


```
%sql --connection_arguments {"timeout":10,"mode":"ro"} sqlite:// SELECT * FROM work;
%sql -a '{"timeout":10, "mode":"ro"}' sqlite:// SELECT * from work;
```

+++

## Connecting to...

Check out our guide for connecting to a database:

- [PostgreSQL](integrations/postgres-connect)

+++

## Connecting securely

**It is highly recommended** that you do not pass plain credentials.

```{code-cell} ipython3
%load_ext sql
```

### DSN connections

```{tip} 
It is recommended to use config file for connection as it's more secure and do not expose credentials.
```

To ensure the security of your credentials, you can store connection information in a configuration file, under a section name chosen to  refer to your database.

For instance, suppose you have a configuration file named _dsn.ini_ that contains the following section:

```
[DB_CONFIG_1] 
drivername=postgres 
host=my.remote.host 
port=5433 
database=mydatabase 
username=myuser 
password=1234
```

then you can establish a connection to your database by running the following commands:

```
%config SqlMagic.dsn_filename='./dsn.ini'
%sql --section DB_CONFIG_1 
```

+++

### Building connection string

One option is to use `getpass`, type your password, build your connection string and pass it to `%sql`:

+++

```python
from getpass import getpass

password = getpass()
connection_string = f"postgresql://user:{password}@localhost/database"
%sql $connection_string
```

+++

### Using `DATABASE_URL`

+++

You may also set the `DATABASE_URL` environment variable, and `%sql` will automatically load it from there. You can do it either by setting the environment variable from your terminal or in your notebook:

```python
from getpass import getpass
from os import environ

password = getpass()
environ["DATABASE_URL"] = f"postgresql://user:{password}@localhost/database"
```

```python
# without any args, %sql reads from DATABASE_URL
%sql
```

+++

## Using an existing `sqlalchemy.engine.Engine`

```{versionadded} 0.5.1
```

Use an existing `Engine` by passing the variable name to `%sql`.

```{code-cell} ipython3
import pandas as pd
from sqlalchemy.engine import create_engine
```

```{code-cell} ipython3
engine = create_engine("sqlite://")
```

```{code-cell} ipython3
df = pd.DataFrame({"x": range(5)})
df.to_sql("numbers", engine)
```

```{code-cell} ipython3
%load_ext sql
```

```{code-cell} ipython3
%sql engine
```

```{code-cell} ipython3
%%sql
SELECT * FROM numbers
```

## Custom Connection

```{versionadded} 0.7.1
```

If you are utilizing an engine that is not explicitly supported by SQLAlchemy, you can still leverage the JupySQL API through a customized connection.

For our example we'll use `QuestDB` which is not supported by SQLAlchemy. If you don't have a QuestDB Server running or you want to spin up one for testing, you can do it with the official [Docker image](https://hub.docker.com/r/questdb/questdb).

```{code-cell} ipython3
%%bash
docker run \
  -p 9000:9000 -p 9009:9009 -p 8812:8812 -p 9003:9003 \
  -v "$(pwd):/var/lib/questdb" \
  questdb/questdb:7.1
```

Ensure that the container is running

```{code-cell} ipython3
%%bash
docker ps
```


Populate it with some data by downloading the penguings dataset

```
from urllib.request import urlretrieve

_ = urlretrieve(
    "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
    "penguins.csv",
)
```

And creating a new table `penguings`

```
df = pd.read_csv("penguins.csv", sep=",")
df.drop_duplicates(subset=None, inplace=True)
df.to_csv("penguins.csv", index=False)

with open("penguins.csv", 'rb') as csv:
    file_data = csv.read()
    files = {'data': ("penguins", file_data)}
    response = requests.post("http://127.0.0.1:9000/imp", files=files)
```

Now, let's establish our connection using 

```{code-cell} ipython3
import psycopg2 as pg
engine = pg.connect(
    "dbname='qdb' user='admin' host='127.0.0.1' port='8812' password='quest'"
)
```

```{note}
We currently support `%sql`, `%sqlplot`, and the `ggplot` API when using custom connection. However, please be advised that there may be some features or functionalities that may not be fully compatible with JupySQL.
```

Connect to JupySQL and pass our custom engine

```{code-cell} ipython3
%load_ext sql
%sql engine
```

Run SQL query

```{code-cell} ipython3
%sql SELECT count(*) FROM "penguins"
```

Use `ggplot` API

```{code-cell} ipython3
(ggplot(diamonds_data, aes(x=x)) + geom_histogram(bins=10, fill="cut"))
```