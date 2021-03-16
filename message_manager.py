from service_files.settings import STATES
from service_files.speeches import (ban_speeches,
                                    registrar_speeches,
                                    authorizer_speeches,
                                    choice_actions_speeches,
                                    start_speeches,
                                    send_file_speeches,
                                    download_file_speeches)

from model_managers import UserManager, AccountManager, FileManager
from FileBot.database_models import Session

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class ProgenitorMessageManager:
    ban_speeches = ban_speeches
    start_speeches = start_speeches

    states = STATES
    session = Session()

    success_text = ''
    failure_text = ''

    success_buttons = []
    failure_buttons = []
    success_markup = []
    failure_markup = []
    ok_buttons = [['OK', 'nothing']]

    user_manager_class = UserManager
    user_manager = None
    user = None

    file_manager_class = FileManager
    file_manager = None
    file_path = None

    account_manager_class = AccountManager
    account_manager = None
    account = None

    def start(self):
        print('start')
        if self.user.current_state == self.states['ban']:
            self.session.close()
            text = self.ban_speeches['ban']
            markup = None
        else:
            self.user_manager.update(
                self.session,
                self.user.id,
                current_state=self.states['input'],
                account_id=''
            )
            self.session.commit()
            self.session.close()

            text = self.start_speeches['welcome']
            buttons = [['Авторизация', 'authorization'],
                       ['Регистрация', 'registration']]
            markup = self.create_buttons(buttons)
        return {'text': text, 'markup': markup, 'file_path': None}

    def end_session_and_returned_response(self):
        self.create_markups()
        response = {'text': '', 'markup': None, 'file_path': None}
        try:
            response = self._commit()
        except Exception as e:
            print(e)
            response = self._rollback()
        finally:
            self.session.close()
            return response

    def create_markups(self):
        if self.failure_buttons:
            self.failure_markup = self.create_buttons(self.failure_buttons)
        if self.success_buttons:
            self.success_markup = self.create_buttons(self.success_buttons)

    def reply_for_blocked_user(self):
        self.success_text += self.ban_speeches['ban']

    def _rollback(self):
        self.session.rollback()
        return {'text': self.failure_text,
                'markup': self.failure_markup,
                'file_path': self.file_path}

    def _commit(self):
        self.session.commit()
        return {'text': self.success_text,
                'markup': self.success_markup,
                'file_path': self.file_path}

    def _set_file_manager(self):
        self.file_manager = self.file_manager_class()

    def _set_account(self, password):
        self.account = self.account_manager.get_object(self.session, password)

    def _create_account(self, password):
        self.account = self.account_manager.create(self.session, password)

    def _set_account_manager(self):
        self.account_manager = self.account_manager_class()

    def _set_user(self, user_id):
        self.user = self.user_manager.get_or_create(self.session, user_id)

    def _set_user_manager(self):
        self.user_manager = self.user_manager_class()

    @staticmethod
    def create_buttons(buttons):
        print(buttons)
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        for button in buttons:
            item = InlineKeyboardButton(button[0], callback_data=button[1])
            markup.add(item)
        return markup


class Registrar(ProgenitorMessageManager):
    reg_speeches = registrar_speeches

    def registration(self, text):
        if text == 'input':
            return self.start()
        elif self.user.current_state == self.states['input']:
            self.registration_first_step()
        elif self.user.current_state == self.states['registration']:
            self.registration_second_step(password=text)

    def registration_first_step(self):
        self.user_manager.update(
            self.session,
            self.user.id,
            current_state=self.states['registration']
        )
        self.success_buttons = [['Отмена', 'input']]
        self.success_text += self.reg_speeches['ask_password']
        self.failure_text += self.reg_speeches['ask_password_fail']

    def registration_second_step(self, password):
        self._create_account(password)
        self.user_manager.update(
            self.session,
            self.user.id,
            account_id=self.account.password,
            current_state=self.states['choice_actions']
        )
        self.success_text += self.reg_speeches['account_created'].format(self.account.password)
        self.success_markup = self.ok_buttons
        self.failure_text += self.reg_speeches['asks_another_password']


class Authorizer(ProgenitorMessageManager):
    auth_speeches = authorizer_speeches

    def authorization(self, password):
        self.success_buttons = [['Отмена', 'input']]
        if password == 'input':
            return self.start()
        elif self.user.current_state == self.states['input']:
            self.authorization_first_step()
        elif self.user.current_state == self.states['authorization']:
            self.authorization_second_step(password)

    def authorization_first_step(self):
        self.user_manager.update(
            self.session,
            self.user.id,
            current_state=self.states['authorization']
        )
        self.success_text += self.auth_speeches['first_good']
        self.failure_text += self.auth_speeches['first_bad']

    def account_exists(self, password):
        self.user_manager.update(
            self.session,
            self.user.id,
            account_id=password,
            error_counter=0,
            current_state=self.states['choice_actions']
        )
        self.success_text += self.auth_speeches['second_good']
        self.failure_text += self.auth_speeches['second_bad']
        self.success_markup = self.ok_buttons

    def account_not_exists(self):
        if self.user.error_counter < 9:
            error_counter = self.user.error_counter + 1
            current_state = self.user.current_state
            self.success_text += self.auth_speeches[
                'third_good'].format(10 - error_counter)
        else:
            error_counter = self.user.error_counter
            current_state = self.states['ban']
        self.user_manager.update(
            self.session,
            self.user.id,
            error_counter=error_counter,
            current_state=current_state
        )

    def authorization_second_step(self, password):
        self._set_account(password)
        if self.account:
            self.account_exists(password)
        else:
            self.account_not_exists()


class ChoiceActions(ProgenitorMessageManager):
    c_a_speeches = choice_actions_speeches
    choice_buttons = [
        ['Отправить файл', 'send_file'],
        ['Загрузить файл', 'download_file'],
        ['Покинуть аккаунт', 'input']
    ]

    def get_choice_actions(self):
        self.success_text += self.c_a_speeches['select_action']
        self.success_buttons = self.choice_buttons

    def change_user_state_to_selected(self, choice):
        self.user_manager.update(
            self.session,
            self.user.id,
            current_state=self.states[choice],
            # account_id=None
        )

    def choice_actions(self, choice):
        if choice not in [i[1] for i in self.choice_buttons]:
            self.get_choice_actions()
        elif choice == 'input':
            return self.start()
        else:
            self.change_user_state_to_selected(choice)


class SendFile(ProgenitorMessageManager):

    def save_file(self, file, file_info):
        try:
            file_name = self.file_manager.save_file(
                self.session,
                self.account.password,
                file_info.file_id,
                file_info.file_unique_id,
                file_info.file_size,
                file_info.file_path,
                file)
            self.success_text = send_file_speeches['saved'].format(file_name)
        except Exception as e:
            print(repr(e))
            self.success_buttons = []
            self.success_text = send_file_speeches['fail']

    def send_file(self, text, file=None, file_info=None):

        if not file and not file_info:
            self.success_buttons = [['Отмена', 'choice_actions']]
            self.success_text += send_file_speeches['send_me_file']
        else:
            self.success_buttons = [['OK', 'choice_actions']]
            self.save_file(file, file_info)


class DownloadFile(ProgenitorMessageManager):
    d_f_speeches = download_file_speeches

    def get_files_query(self):
        return self.file_manager.get_query(self.session, self.account.password)

    def get_files_list(self, files):
        return [[i.file_name, str(i.id)] for i in files]

    def get_file_full_path(self, pk):
        print('pk', pk)
        relative_path = self.file_manager.get_object(self.session, pk).file_path
        print('relative_path', relative_path)
        return self.file_manager.get_full_path(relative_path)

    def provide_choice_of_files(self, files):
        self.success_buttons = [['Отмена', 'choice_actions']]
        self.success_buttons += self.get_files_list(files)
        self.success_text += self.d_f_speeches['select_file']

    def provide_the_selected_file(self, pk):
        self.success_buttons = [['Продолжить', 'nothing']]
        self.file_path = self.get_file_full_path(int(pk))
        print(self.file_path)
        self.user_manager.update(
            self.session,
            self.user.id,
            current_state=self.states['choice_actions'])

    def download_file(self, text):
        print('download_file')
        files = self.get_files_query()
        print(files)
        if files:
            print('files')
            if text not in [str(i.id) for i in files]:
                print('text not in [str(i.id) for i in files]')
                self.provide_choice_of_files(files)
            else:
                print('text in [str(i.id) for i in files]')
                self.provide_the_selected_file(text)
        else:
            self.success_buttons = [['Понятно', 'choice_actions']]
            self.success_text += self.d_f_speeches['files_not_found']


class MessageManager(Authorizer, Registrar, ChoiceActions, SendFile, DownloadFile):

    def __init__(self, user_id):
        self._set_user_manager()
        self._set_user(user_id)
        self._set_account_manager()
        if self.user.account_id:
            self._set_account(self.user.account_id)
            self._set_file_manager()
            print(self.account)

    def dispatch(self, text=None, file=None, file_info=None):
        print()
        print('dispatch')
        print(self.user.current_state)
        # print(file)
        # print()
        # print(file_info)
        # print()
        # print(text)
        # print()

        if text == 'input' and self.user.current_state in [1, 2, 3, 4]:
            return self.start()

        if text == 'choice_actions' and self.user.current_state in [5, 6]:
            self.change_user_state_to_selected(text)

        if text == 'registration' or self.user.current_state == self.states['registration']:
            print('registration')
            self.registration(text)

        if text == 'authorization' or self.user.current_state == self.states['authorization']:
            print('authorization')
            self.authorization(text)

        if self.user.current_state == self.states['choice_actions']:
            print('choice_actions')
            self.choice_actions(text)

        if self.user.current_state == self.states['send_file']:
            print('send_file')
            self.send_file(text, file, file_info)

        if self.user.current_state == self.states['download_file']:
            print('download_file')
            self.download_file(text)

        return self.end_session_and_returned_response()
