from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GeneratedImage(db.Model):
    volume_id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer)
    volume_name = db.Column(db.String(256), index=True, unique=True)
    processed_flag = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Volume {}>'.format(self.volume_name)    