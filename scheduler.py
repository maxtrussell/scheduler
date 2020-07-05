from app import app, db
from app.models import (
    User,
    Event,
    Time,
    Commitment,
    Transaction,
    Account,
    Treasure,
)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'Time': Time,
        'Commitment': Commitment,
        'Transaction': Transaction,
        'Account': Account,
        'Treasure': Treasure,
    }
