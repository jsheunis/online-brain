from flask_sqlalchemy import SQLAlchemy

# Define the SQLAlchemy instance here in order to avoid circular imports
db = SQLAlchemy()


class GeneratedImage(db.Model):
    volume_id = db.Column(db.Integer, primary_key=True)
    experiment_name = db.Column(db.ForeignKey('experiment.experiment_name'))
    volume_name = db.Column(db.String(256), index=True)
    sprite_b64 = db.Column(db.Text())
    sprite_json = db.Column(db.Text())
    stat_map_b64 = db.Column(db.Text(), nullable=True)
    colormap_b64 = db.Column(db.Text(), nullable=True)

    def __repr__(self):
        return '<Volume {}>'.format(self.volume_name)


class Experiment(db.Model):
    experiment_id = db.Column(db.Integer, primary_key=True)
    experiment_name = db.Column(db.String(128), index=True, unique=True)
    number_of_volumes = db.Column(db.Integer)
    repetition_time = db.Column(db.Integer)

    def __repr__(self):
        return '<Experiment {}>'.format(self.experiment_name)
