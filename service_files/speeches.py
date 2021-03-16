
ban_speeches = {'ban': 'Вы заблокированы, любые действия будут проигнорированы\n\n'}

registrar_speeches = {
    'ask_password': 'Введите пароль\n\nВ пароле доступны любые символы\n\nЧем больше символов, тем надежнее будут храниться ваши данные\n\n',
    'ask_password_fail': 'Что-то попшло не так, введите команду: /start\n\n',
    'account_created': 'Вы создали новый аккаунт\n\nДоступ к аккаунту осуществляется по введенному Вами паролю:\n\n{}\n\nСохраните пароль в надежном месте и не сообщайте его посторонним лицам\n\n',
    'asks_another_password': 'Что-то пошло не так, попробуйте ввести другой пароль\n\n'
}

authorizer_speeches = {
    'first_good': 'Введите пароль\n\n',
    'first_bad': 'Что-то пошло не так, введите команду /start\n\n',
    'second_good': 'Пароль принят\nВход выполнен\n\n_______________\n\nУ вас есть возможность хранить здесь файлы объемом до 10 Mb.\nТак же вы можете скачивать файлы \n\n',
    'second_bad': 'Что-то пошло не так, введите это-же пароль еще раз\n\n',
    'third_good': 'Пароль неверный, у вас осталось {} попыток до блокировки',
}

choice_actions_speeches = {
    'select_action': 'Выберете действие',
    'select_download_file': '',
    'select_send_file': ''
}

start_speeches = {
    'welcome': 'Здравствуте!\nВыберете действие:'
}

bot_service_speeches = {
    'file_is_too_big': 'Файл слишком большой: {} byte \n\nВыберете файл меньшего объема, до 10485760 b'
}

send_file_speeches = {
    'send_me_file': 'Выберете и отправьте файл.\n\nВнимание размер файла не должен превышать 10 Mb',
    'saved': 'Ваш файл сохранен под названием {}',
    'fail': 'не удалось сохранить файл, попробуйте еще раз'
}

download_file_speeches = {
    'files_not_found': 'Файлы не обнаружены, сначала нужно добаыить хотя-бы один',
    'select_file': 'Ниже представлены ваши файлы\n\nДля получения нужного, нажмите на него',
}
