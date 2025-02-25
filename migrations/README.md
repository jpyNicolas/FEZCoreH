# **Alembic Migration Environment Script (`FEZCore/migrations/env.py`)**

## **Overview**
This script configures **Alembic**, a database migration tool for SQLAlchemy, to apply schema changes to the database. It allows running migrations in **offline mode** (generating SQL scripts without a database connection) and **online mode** (executing migrations with a live database connection).  

The script does the following:  
- Sets up logging based on the Alembic configuration.  
- Loads the SQLAlchemy **metadata** from multiple model modules.  
- Determines whether migrations should be run **offline** or **online**.  
- Configures and executes the migrations accordingly.  

---

## **Script Breakdown**

### **1. Importing Required Modules**
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
```
- **`fileConfig`**: Sets up logging from the Alembic config file.  
- **`engine_from_config` & `pool`**: Used to create a database connection.  
- **`context`**: The Alembic migration context, responsible for running migrations.  
- **`settings`**: Imports the database connection settings from the application configuration.  

---

### **2. Load Alembic Configuration**
```python
config = context.config
```
- Loads the **Alembic configuration object**, which contains settings from `alembic.ini`.  

#### **Logging Setup**
```python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
```
- Configures logging based on the Alembic **`.ini`** file, if available.

---

### **3. Define Target Metadata**
```python
from app.models import Base
from app.auth.models import Base as AuthBase
from app.utils.caching_files.models import Base as FileCacheBase

target_metadata = [Base.metadata, AuthBase.metadata, FileCacheBase.metadata]
```
- **Why?** Alembic uses **SQLAlchemy metadata** to detect changes in database schemas.
- **What?** It imports metadata from multiple modules:
  - `Base.metadata` from `app.models`
  - `AuthBase.metadata` from `app.auth.models`
  - `FileCacheBase.metadata` from `app.utils.caching_files.models`
- **Effect:** Ensures all models are included in migrations.

---

## **4. Running Migrations**

### **4.1 Offline Mode**
```python
def run_migrations_offline() -> None:
```
- **Purpose:** Generates **SQL migration scripts** without requiring a live database connection.
- **Use Case:** Useful for generating scripts that can be executed later.

#### **Key Configuration**
```python
url = settings.sqlalchemy_database_url
context.configure(
    url=url,
    target_metadata=target_metadata,
    literal_binds=True,
    dialect_opts={"paramstyle": "named"},
)
```
- **Uses the database URL** from `settings.sqlalchemy_database_url`.  
- **Includes metadata** so Alembic can detect schema changes.  
- **Sets `literal_binds=True`** to include actual values in the generated SQL instead of placeholders.  

#### **Executing Migrations**
```python
with context.begin_transaction():
    context.run_migrations()
```
- Starts a **transaction** and applies migrations.

---

### **4.2 Online Mode**
```python
def run_migrations_online() -> None:
```
- **Purpose:** Runs migrations directly on a **live database connection**.
- **Use Case:** Applies migrations immediately to the database.

#### **Create Database Connection**
```python
configuration = config.get_section(config.config_ini_section, {})
configuration["sqlalchemy.url"] = settings.sqlalchemy_database_url
connectable = engine_from_config(
    configuration,
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
```
- Fetches the **database URL** from `settings.sqlalchemy_database_url`.  
- Creates an **SQLAlchemy Engine** with `NullPool` (disables connection pooling).  

#### **Apply Migrations**
```python
with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()
```
- Establishes a **database connection**.
- Configures Alembic **with the connection and metadata**.
- **Begins a transaction** and runs the migrations.

---

### **5. Determine the Migration Mode**
```python
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```
- **Automatically detects** if Alembic is running in **offline** or **online** mode.
- Calls the appropriate function (`run_migrations_offline()` or `run_migrations_online()`).

---

## **Summary of Migration Modes**
| Mode         | Description |
|-------------|------------|
| **Offline** | Generates SQL migration scripts without executing them. |
| **Online**  | Directly applies migrations using a live database connection. |

---

## **Conclusion**
This script ensures that **database schema migrations** are correctly applied by **Alembic** while supporting both **offline script generation** and **online execution**. It dynamically loads metadata, configures database connections, and applies schema changes efficiently. 🚀
