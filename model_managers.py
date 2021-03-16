from FileBot.database_models import Account, User, File
from datetime import date

import os

from service_files.settings import STATES, FILES_DIR, BASE_DIR


class AbstractManager:
    model = None

    def get_object(self, session, pk):
        return session.query(self.model).get(pk)


class UserManager(AbstractManager):
    model = User

    def create(self, session, user_id):
        user = self.model(
            id=user_id,
            error_counter=0,
            current_state=STATES['input']
        )
        session.add(user)
        return user

    def update(self, session, user_id, account_id=None, current_state=None, error_counter=None):
        user = self.get_object(session, user_id)
        if user:
            if account_id or account_id == '':
                user.account_id = account_id
            if current_state or current_state == 0:
                user.current_state = current_state
            if error_counter or error_counter == 0:
                user.error_counter = error_counter

    def get_or_create(self, session, user_id):
        user = self.get_object(session, user_id)
        if not user:
            user = self.create(session, user_id)
        return user


class AccountManager(AbstractManager):
    model = Account

    def create(self, session, password):
        account = self.model(password=password)
        session.add(account)
        return account

    def get_or_create(self, session, password):
        account = self.get_object(session, password)
        if not account:
            account = self.create(session, password)
        return account


class FileDataBaseManager(AbstractManager):
    model = File

    def create(self, session, account_id, file_id, file_unique_id, file_size, file_name, file_path):
        file = self.model(
            account_id=account_id,
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_size=file_size,
            file_name=file_name,
            file_path=file_path
        )
        session.add(file)

    def get_query(self, session, account_id):
        return session.query(self.model).filter_by(account_id=account_id)


class FilePathManager:
    base_dir = BASE_DIR
    files_dir = FILES_DIR

    def make_dir_if_not_exists(self, full_path_to_dir):
        if not os.path.exists(full_path_to_dir):
            self.make_dir(full_path_to_dir)

    def make_dir(self, full_path_to_dir):
        os.makedirs(full_path_to_dir)

    def get_relative_path_to_dir(self):
        year = str(date.today().year)
        month = str(date.today().month)
        day = str(date.today().day)
        return os.path.join(self.files_dir, year, month, day)

    def get_relative_path_to_file(self, relative_path_to_dir, file_name):
        relative_path = os.path.join(relative_path_to_dir, file_name)
        return os.path.normpath(relative_path)

    def get_full_path(self, relative_path):
        print(relative_path)
        return os.path.join(self.base_dir, relative_path)


class FileManager(FilePathManager, FileDataBaseManager):

    def name_normalize(self, file_name):
        for i in range(len(file_name)):
            if file_name[i] == '/':
                head = file_name[:i]
                tail = file_name[i+1:]
                file_name = head + '_' + tail
        return file_name

    def save_file(self, session, account_id, file_id, file_unique_id, file_size, file_name, file):
        file_name = self.name_normalize(file_name)

        relative_path_to_dir = self.get_relative_path_to_dir()
        full_path_to_dir = self.get_full_path(relative_path_to_dir)
        self.make_dir_if_not_exists(full_path_to_dir)

        relative_path_to_file = self.get_relative_path_to_file(relative_path_to_dir, file_name)
        full_path_to_file = self.get_full_path(relative_path_to_file)

        self.create(session, account_id, file_id, file_unique_id, file_size, file_name, relative_path_to_file)
        self.file_write(file, full_path_to_file)

        return file_name

    def file_write(self, file, full_path):
        full_path = r'' + full_path
        print(type(full_path))
        with open(full_path, 'wb') as f:
            f.write(file)

"""
with open(r"D:\test.txt", "w") as file:
    file.writelines("%s\n" % line for line in lines)
"""


