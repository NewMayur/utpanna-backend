import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables
load_dotenv()

def get_database_uri(env_var_name):
    uri = os.getenv(env_var_name)
    if not uri:
        raise ValueError(f"Environment variable {env_var_name} is not set")
    return uri

try:
    # SQLite database connection
    sqlite_uri = get_database_uri('SQLALCHEMY_DATABASE_URI')
    sqlite_engine = create_engine(sqlite_uri)
    sqlite_metadata = MetaData()
    sqlite_metadata.reflect(bind=sqlite_engine)

    # MySQL database connection
    mysql_uri = get_database_uri('MYSQL_DATABASE_URI')
    mysql_engine = create_engine(mysql_uri.replace('mysql://', 'mysql+mysqlconnector://'), connect_args={'auth_plugin': 'mysql_native_password'})
    mysql_metadata = MetaData()
    mysql_metadata.reflect(bind=mysql_engine)
except ValueError as e:
    print(f"Error: {str(e)}")
    exit(1)
except Exception as e:
    print(f"Error connecting to databases: {str(e)}")
    exit(1)

def migrate_table(table_name):
    print(f"Migrating table: {table_name}")
    sqlite_table = Table(table_name, sqlite_metadata, autoload=True, autoload_with=sqlite_engine)
    mysql_table = Table(table_name, mysql_metadata, autoload=True, autoload_with=mysql_engine)

    sqlite_session = sessionmaker(bind=sqlite_engine)()
    mysql_session = sessionmaker(bind=mysql_engine)()

    try:
        # Fetch all rows from SQLite
        rows = sqlite_session.query(sqlite_table).all()

        # Insert rows into MySQL
        for row in rows:
            data = {column.name: getattr(row, column.name) for column in sqlite_table.columns}
            mysql_session.execute(mysql_table.insert().values(data))

        mysql_session.commit()
        print(f"Successfully migrated {len(rows)} rows from {table_name}")
    except Exception as e:
        mysql_session.rollback()
        print(f"Error migrating table {table_name}: {str(e)}")
    finally:
        sqlite_session.close()
        mysql_session.close()

def main():
    try:
        # Get all table names
        table_names = sqlite_metadata.tables.keys()

        # Migrate each table
        for table_name in table_names:
            migrate_table(table_name)

        print("Migration completed successfully")
    except Error as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()