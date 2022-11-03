import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth


TIME_SEGMENTS = [
    (8, 12),
    (12, 16),
    (16, 20),
    (20, 24)
]


def db_init():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


def get_user_prefs(db):
    users_ref = db.collection(u"user-preferences")
    docs = users_ref.stream()
    user_prefs = {}
    for doc in docs:
        user_prefs[doc.id] = doc.to_dict()
    return user_prefs


def get_user_email(uuid):
    user = auth.get_user(uuid)
    return user.email


def get_users():
    """Get users on this app.
    The following attributes are retrieved:
        uuid
        email
        timeSegments - the time segments that the user wants to receive notifications
    """
    db = db_init()
    user_prefs = get_user_prefs(db)
    users = []
    for uuid, user_pref in user_prefs.items():
        users .append({
            "uuid": uuid,
            "email": get_user_email(uuid),
            "timeSegments": [segment for segment in TIME_SEGMENTS if user_pref["notificationStartTime"] <= segment[0] and segment[1] <= user_pref["notificationEndTime"]]
        })
    return users


def main():
    get_users()


if __name__ == "__main__":
    main()
