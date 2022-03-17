from models import app_models, db


def migrate_db():

    db.connect()
    db.create_tables(app_models)
    db.close()


if __name__ == "__main__":
    migrate_db()
