from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bank.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0)''')
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    def create_user(self, username, password):
        try:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, 0)", (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_balance(self, username, amount):
        self.cursor.execute("UPDATE users SET balance=balance+? WHERE username=?", (amount, username))
        self.conn.commit()

class LoginScreen(Screen):
    def verify_credentials(self, username, password):
        app = App.get_running_app()  # Access the running instance of BankApp
        user = app.db.get_user(username)
        if user and user[1] == password:
            if username == 'admin':
                self.manager.current = 'admin'
            else:
                self.manager.current = 'user'
        else:
            self.ids.error_label.text = 'Invalid username or password'
            
class SignUpScreen(Screen):
    def sign_up(self, username, password):
        if app.db.create_user(username, password):
            self.manager.current = 'login'
        else:
            self.ids.error_label.text = 'Username already exists'

class AdminPanel(Screen):
    pass

class UserPanel(Screen):
    def deposit(self, amount):
        app.db.update_balance('user', amount)
        self.ids.balance_label.text = f'Balance: ${app.db.get_user("user")[2]}'
        self.ids.error_label.text = ''

    def withdraw(self, amount):
        user = app.db.get_user('user')
        if user[2] >= amount:
            app.db.update_balance('user', -amount)
            self.ids.balance_label.text = f'Balance: ${app.db.get_user("user")[2]}'
            self.ids.error_label.text = ''
        else:
            self.ids.error_label.text = 'Insufficient balance'

class BankApp(App):
    def build(self):
        self.db = Database()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(AdminPanel(name='admin'))
        sm.add_widget(UserPanel(name='user'))
        return sm

    def on_stop(self):
        self.db.close()

if __name__ == '__main__':
    app = BankApp()
    app.run()
