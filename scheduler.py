from app import app, db
from app.models import User, Event, Time, Commitment

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'Time': Time,
        'Commitment': Commitment,
    }
