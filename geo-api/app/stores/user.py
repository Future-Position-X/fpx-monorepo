import bcrypt
from app.stores.base_store import Store
from app.models.user import User


class UserStore(Store):
    def insert(self, user):
        c = self.cursor()
        c.execute("""
            INSERT INTO users(
                provider_uuid,
                email,
                password
            ) VALUES (
                %(provider_uuid)s,
                %(email)s,
                %(password)s
            )
            RETURNING uuid;
            """, {
            "provider_uuid": user.provider_uuid,
            "email": user.email,
            "password": bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        })
        return c.fetchone()["uuid"]

    def get_by_uuid(self, user_uuid):
        c = self.cursor()
        c.execute("""
            SELECT * FROM users
            WHERE uuid = %(user_uuid)s
            """, {
                "user_uuid": user_uuid
            })

        return User(**c.fetchall()[0])


    def get_by_email(self, email):
        c = self.cursor()
        c.execute("SELECT * FROM users WHERE email = %(email)s", {
            "email": email
        })

        return User(**c.fetchall()[0])


    def update(self, user_uuid, user):
        c = self.cursor()
        c.execute("""
            UPDATE users SET
            provider_uuid = %(provider_uuid)s,
            email = %(email)s,
            password = %(password)s
            WHERE uuid = %(user_uuid)s
            """, {
                "provider_uuid": user.provider_uuid,
                "email": user.email,
                "password": bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                "user_uuid": user_uuid
            })

    def delete(self, user_uuid):
        c = self.cursor()
        c.execute("DELETE FROM users WHERE uuid = %(user_uuid)s", {
            "user_uuid": user_uuid
        })