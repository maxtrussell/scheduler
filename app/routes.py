from flask import (
    flash,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    login_required,
    logout_user,
)
from werkzeug.urls import url_parse

from app import (
    app,
    db,
    errors,
)
import app.discord as discord
from app.forms import (
    EventForm,
    LoginForm,
    RegistrationForm,
    NewEventForm,
    EditEventForm,
)
from app.models import (
    Event,
    User,
    Time,
    Commitment,
    Transaction,
    Account,
    Treasure,
)
from config import Config

@app.route('/')
@login_required
def index():
    # sory events in descending order
    events = Event.query.order_by(Event.timestamp.desc()).all()
    return render_template('index.html', title='Home', events=events)

@app.route('/login', methods=["GET", "POST"])
def login():
    # Skip if user already auth'd
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # login failed
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # login succeeded
        login_user(user, remember=form.remember_me.data)

        # get next page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

class TimeChoice:
    def __init__(self, users, time):
        self.users = users
        self.users_str = ', '.join(self.users)
        self.time = time
        self.checked = current_user.username in self.users

@app.route('/event/<event_id>', methods=['GET', 'POST'])
@login_required
def event(event_id):
    form = EventForm()
    event = Event.query.get_or_404(event_id)
    times = Time.query.filter_by(event_id=event.id).all()
    initial_quorum  = any([True for time in times if quorum(time)])
    if request.method == 'POST':
        suggested_times = form.suggested_times.data
        if suggested_times != "":
            # User suggested times
            for description in suggested_times.split(','):
                description = description.strip()
                if description == '':
                    continue
                # 1. Add time to event
                suggested_time = Time(event=event, description=description)
                db.session.add(suggested_time)
                try:
                    db.session.commit()
                except Exception as e:
                    flash('Error: Your response was not recorded')
                    app.logger.error(str(e))
                    return redirect(url_for('event', event_id=event_id))

                # 2. Add commitment
                commitment = Commitment(user=current_user, time=suggested_time)
                db.session.add(commitment)

        # Already existing times
        commitments = Commitment.query.filter_by(user=current_user).all()
        for time in times:
            commitment = Commitment.query.filter_by(
                user=current_user,
                time=time,
            ).first()
            if time.description in request.form and not commitment:
                # 1. unavailable -> available
                commitment = Commitment(user=current_user, time=time)
                db.session.add(commitment)
            elif commitment and time.description not in request.form:
                # 2. available -> unavailable
                db.session.delete(commitment)
            
        db.session.commit()
        flash('Thank you, your repsonse has been submitted!')

        times = Time.query.filter_by(event_id=event.id).all()
        quorum_times = [time for time in times if quorum(time)]
        if quorum_times:
            msg = (
                f"Quorum is met for '{event.description}' "
                f"at the following times:"
            )
            for quorum_time in quorum_times:
                users = [c.user.username for c in quorum_time.commitments.all()]
                msg += f"\n\t- {quorum_time.description} with {users}"
            discord.message(msg)
        elif initial_quorum:
            discord.message(
                f"Quorum is no longer met for '{event.description}'"
            )

        return redirect(url_for('event', event_id=event_id))
        
    existing_times = []
    for time in times:
        commitments = Commitment.query.filter_by(time_id=time.id).all()
        existing_times.append(TimeChoice(
            [c.user.username for c in commitments],
            time.description,
        ))
    return render_template(
        'event.html',
        title=event.description,
        form=form,
        event=event,
        existing_times=existing_times,
        has_perms=has_perms,
    )

@app.route('/event/<event_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if not has_perms(event.owner):
        flash('Insufficient permissions')
        return redirect(url_for('event', event_id=event_id))
    if request.method == 'POST':
        db.session.delete(event)
        db.session.commit()
        flash('Event successfully deleted!')
        return redirect(url_for('index'))
    return render_template('delete_event.html', event=event)

@app.route('/event/<event_id>/post', methods=['POST'])
@login_required
def post_event(event_id):
    event = Event.query.get_or_404(event_id)
    discord.message(
        f'@everyone Event "{event.description}" has been created. '
        f'Please fill it out here: https://dnd.maxtrussell.duckdns.org/event/{event.id}'
    )
    return redirect(url_for('event', event_id=event_id))

@app.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = NewEventForm()
    if form.validate_on_submit():
        # TODO: Make event description unique
        event = Event(owner=current_user, description=form.description.data)
        db.session.add(event)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(str(e))
            flash('Event creation failed')
            return redirect(url_for('create_event'))

        flash(f'Successfully created event "{event.description}"!')
        return redirect(url_for('event', event_id=event.id))
    return render_template('create_event.html', title='Create Event', form=form)

@app.route('/event/<event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    form = EditEventForm()
    event = Event.query.get_or_404(event_id)
    times = Time.query.filter_by(event_id=event.id).all()
    if not has_perms(event.owner):
        flash('Insufficient permissions')
        return redirect(url_for('event', event_id=event_id))

    if request.method == 'POST':
        event.description = form.description.data
        for time in times:
            if time.description in request.form:
                db.session.delete(time)
        db.session.commit()
        flash('Successfully edited event!')
        return redirect(url_for('event', event_id=event_id))

    existing_times = []
    for time in times:
        commitments = Commitment.query.filter_by(time_id=time.id).all()
        existing_times.append(TimeChoice(
            [c.user.username for c in commitments],
            time.description,
        ))
    return render_template(
        'edit_event.html',
        title=f'Edit "{event.description}"',
        form=form,
        event=event,
        existing_times=existing_times,
    )

@app.route('/vault')
@login_required
def vault():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    account = Account.query.get(1)
    treasure = Treasure.query.order_by(Treasure.timestamp.desc()).all()
    return render_template(
        'vault.html',
        title='Vault',
        account=account,
        transactions=transactions,
        treasure=treasure,
    )

@app.route('/vault/transaction', methods=['POST'])
@login_required
def add_transaction():
    pp = 0 if not request.form['pp'] else int(request.form['pp'])
    gp = 0 if not request.form['gp'] else int(request.form['gp'])
    ep = 0 if not request.form['ep'] else int(request.form['ep'])
    sp = 0 if not request.form['sp'] else int(request.form['sp'])
    cp = 0 if not request.form['cp'] else int(request.form['cp'])
    if request.form['transaction_type'] == "Withdrawal":
       pp *= -1
       gp *= -1
       sp *= -1
       ep *= -1
       cp *= -1

    prev_total = 0
    prev_transaction = Transaction.query.order_by(Transaction.timestamp.desc()).first()
    if prev_transaction:
        prev_total = prev_transaction.running_total
    transaction = Transaction(
        user_id=current_user.id,
        description=request.form['description'],
        platinum=pp,
        gold=gp,
        electrum=ep,
        silver=sp,
        copper=cp,
        running_total=prev_total + \
            copper_value(pp, gp, ep, sp, cp) / 100.0,
    )
    # TODO: hack
    account = Account.query.get(1)
    account.platinum += transaction.platinum
    account.gold += transaction.gold
    account.electrum += transaction.electrum
    account.silver += transaction.silver
    account.copper += transaction.copper

    db.session.add(transaction)
    try:
        db.session.commit()
    except Exception as e:
        flash ('Transaction failed')
        app.logger.error(str(e))
        db.session.rollback()
        return redirect(url_for('vault'))
    flash('Transaction recorded successfully!')
    return redirect(url_for('vault'))

@app.route('/vault/treasure', methods=['POST'])
@login_required
def add_treasure():
    treasure = Treasure(
        description=request.form["description"],
        value=int(request.form["value"])
    )
    db.session.add(treasure)
    db.session.commit()
    flash('Successfully added treasure!')
    return redirect(url_for('vault'))

@app.route('/vault/treasure/delete', methods=['POST'])
@login_required
def delete_treasure():
    treasure = Treasure.query.get(int(request.form['treasure_id']))
    db.session.delete(treasure)
    db.session.commit()
    flash('Successfully deleted treasure!')
    return redirect(url_for('vault'))

@app.route('/vault/treasure/sell', methods=['POST'])
@login_required
def sell_treasure():
    treasure = Treasure.query.get(int(request.form['treasure_id']))

    prev_total = 0
    prev_transaction = Transaction.query.order_by(Transaction.timestamp.desc()).first()
    if prev_transaction:
        prev_total = prev_transaction.running_total

    pp, gp, ep, sp, cp = make_change(treasure.value * 100)
    description = f'Sold "{treasure.description}"'
    transaction = Transaction(
        description=description,
        platinum=pp,
        gold=gp,
        electrum=ep,
        silver=sp,
        copper=cp,
        running_total=prev_total + \
            copper_value(pp, gp, ep, sp, cp) / 100.0,
    )

    # TODO: hack
    account = Account.query.get(1)
    account.platinum += transaction.platinum
    account.gold += transaction.gold
    account.electrum += transaction.electrum
    account.silver += transaction.silver
    account.copper += transaction.copper

    db.session.add(transaction)
    db.session.delete(treasure)
    db.session.commit()

    flash('Successfully sold treasure!')
    return redirect(url_for('vault'))

def has_perms(owner):
    return (current_user.username in app.admins
            or current_user.username == owner.username)

def make_change(cp):
    denominations = [1000, 100, 50, 10]
    change = []
    for denomination in denominations:
        change.append(cp // denomination)
        cp = cp % denomination
    change.append(cp)
    return change

def copper_value(pp, gp, ep, sp, cp):
    return (1000 * pp
            + 100 * gp
            + 50 * ep
            + 10 * sp
            + 1 * cp)

def quorum(time):
    commitments = time.commitments.all()
    if len(commitments) >= Config.QUORUM_THRESHOLD:
        usernames = [User.query.get_or_404(c.user_id).username for c in commitments]
        if Config.DM_USER in usernames:
            return True
    return False
