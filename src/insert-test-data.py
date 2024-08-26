from os import getenv
from api.models import db, User
from flask_migrate import Migrate
from sqlalchemyseeder import ResolvingSeeder
from flask import Flask
app = Flask(__name__)


db_url = getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

seeder = ResolvingSeeder(db.session)
seeder.register(User)
new_entities = seeder.load_entities_from_json_file(getenv("SEED_DATA"))
db.session.commit()
