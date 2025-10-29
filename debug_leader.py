from app import create_app
app = create_app()
app.app_context().push()
from app.models.leader import Leader
from app.models.user import User
leaders = Leader.query.all()
for l in leaders:
    user = User.query.get(l.user_id)
    print(f'Leader {l.id}: user_id={l.user_id}, user exists: {user is not None}')
    if user:
        print(f'  User: {user.username}, role: {user.role}')
    else:
        print('  User does not exist!')
