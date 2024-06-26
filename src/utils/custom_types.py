from enum import Enum
from typing import NamedTuple

class BotStatusEnum(Enum):
    """
    Статус работы бота
    """
    ON  = 'on'  # Бот запущен:
                #  - Устанавливается администратором в случае если бот должен работать в обычном режиме
                #  - Устанавливается самим ботом после перезагрузки
    OFF = 'off' # Бот выключен - отключатся процесс бота, устанавливается администратором

    SERVICE = 'service' # Сервисный режим - бот отправляет уведомление о том, что он находится в сервисном режиме при любом взаимодействии
    
    RESTART    = 'restart'    # Команда на перезапуск, устанавливается администратором
    RESTARTING = 'restarting' # Состояние перезапуска, устанавливается ботом при выключением перед перезагрузкой

class GroupStatusEnum(Enum):
    """
    Статус группы для управления доступом
    """
    INACTIVE    = 'inactive'    # Не актвная группа
    NORMAL      = 'normal'      # Обычная группа
    ADMIN       = 'admin'       # Группа администраторов:
                                #  - приходят оповещения об отправке уведомлений
                                #  - приходят оповещения о количестве зарегестрированных пользователей
    SUPER_ADMIN = 'super_admin' # Группа суперадминистраторов, помимо функций обычных администраторов:
                                #  - приходят уведомления о запланированных уведомлениях
                                #  - приходят уведомления об ошибках в боте

class UserStatusEnum(Enum):
    """
    Статус пользователей
    """
    INACTIVE = 'inactive' # Не актвный пользователь
    ACTIVE   = 'active'   # Обычный пользователь

class FieldBranchStatusEnum(Enum):
    """
    Статус поля пользователя 
    """
    INACTIVE   = 'inactive' # Не активная ветка
    NORMAL     = 'normal'   # Нормальная ветка

class FieldStatusEnum(Enum):
    """
    Статус поля пользователя 
    """
    INACTIVE   = 'inactive' # Не актвное поле
    NORMAL     = 'normal'   # Нормальный вопрос

class ReplyTypeEnum(Enum):
    """
    Тип ответа на сообщения
    """
    BRANCH_START     = 'branch_start'
    FULL_TEXT_ANSWER = 'full_text_answer'
    FAST_ANSWER      = 'fast_answer'
    
    
class KeyboardKeyStatusEnum(Enum):
    """
    Статус кнопки на клавиатуре
    """
    INACTIVE = 'inactive' # Не актвная клавиша - не отображается
    NORMAL   = 'normal'   # Обычная клавиша
    DEFERRED = 'deferred' # Вернуться к отложенному вопросу - отображается только когда у пользователя заполненно поле отложенного вопроса
    ME       = 'me'       # Посмотреть свою пользовательскую запись (основные и откладываемые вопросы)

class NotificationStatusEnum(Enum):
    """
    Статус отправки уведомлений
    """
    INACTIVE   = 'inactive'
    TO_DELIVER = 'to_deliver'
    PLANNED    = 'planned'
    DELIVERED  = 'delivered'

class UserFieldDataPlain(NamedTuple):
    key:   str
    value: str

class UserFieldDataPrepared(NamedTuple):
    value: str
    document_bucket: str
    image_bucket:    str

class UserDataPrepared(NamedTuple):
    id:       int
    chat_id:  int
    username: str
    fields:   dict[int, UserFieldDataPrepared]