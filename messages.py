from typing import List, Literal

from aiogram.types import InlineKeyboardButton as IButton, Message
from pydantic import BaseModel, model_validator

import config


class MsgModel(BaseModel):
    id: int
    message: Message | None = None
    text: str | None = None
    message_id: int | None = None
    markup: List[List[IButton]] | None = None
    photo_type: Literal['file_id', 'filename'] = 'filename'
    photo: str | None = None
    reply_to_message_id: int | None = None
    disable_notifications: bool = False
    disable_web_page_preview: bool = True
    parse_mode: str = 'html'
    photo_name: str | None = None

class StartMessage(MsgModel):
    """text.format: first_name"""
    text: str = """
Привет, {first_name} 👋

С помощью этого бота ты можешь получить доступ в закрытое сообщество ATRUMS.
Выбирай нужный раздел через кнопки ниже ⬇️
    """
    markup: List[List[IButton]] = [
        [IButton(text='Получить доступ', callback_data='get_access')],
        [IButton(text='Моя подписка', callback_data='my_subscribe')],
        [IButton(text='Тех. поддержка', callback_data='support')],
        [IButton(text='Реферальная система', callback_data='referral')],
        [IButton(text='Что есть в закрытом сообществе', callback_data='more_info')],
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'start'

class GetAccess(MsgModel):
    text: str = """
Какой срок?
    """
    markup: List[List[IButton]] = [
        [IButton(text='1 месяц 80$', callback_data='get_access/1_month/crypto')],
        [IButton(text='3 месяца 200$', callback_data='get_access/3_month/crypto')],
        [IButton(text='6 месяцев 400$', callback_data='get_access/6_month/crypto')],
    ]

class GetAccessXMonth(MsgModel):
    text: str = """
        Выберите способ оплаты
    """
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'payment_type'

class PayAccessCrypto(MsgModel):
    """text.format: day_count pay_amount"""
    text: str = """
Период подписки: {day_count} дней

Стоимость: {pay_amount}$
    """

class PayAccessRubles(PayAccessCrypto):
    """text.format: day_count pay_amount"""
    text: str = """
Период подписки: {day_count} дней

Стоимость: {pay_amount} руб.

Нажми на номер карты, чтобы скопировать.
Номер карты: <blockquote><code>2200300136401849</code></blockquote>

<i>Если у вас есть <b>ПРОМОКОД</b>, сначала напишите его</i>

После оплаты - отправьте чек в чат👇

<i>Фото чека должно быть отправлено фоткой, а не файлом</i>
    """

class PayError(MsgModel):
    text: str = """
Не увидели твоего перевода, если вы произвели оплату напишите в тех. поддержку
    """

    markup: List[List[IButton]] = [
        [IButton(text='Тех. поддержка', callback_data='support')]
    ]

class PaySuccess(MsgModel):
    text: str = """
Закрытые чаты уже ждут тебя 👇
    """

class RublesAfterPayInfo(MsgModel):
    text: str = """
Мы проверяем перевод, отправим ответ в ближайшее время
    """

    markup: List[List[IButton]] = [
        [IButton(text='Тех. поддержка', callback_data='support')],
        [IButton(text='Моя подписка', callback_data='my_subscribe')],
        [IButton(text='Реферальная система', callback_data='referral')],
    ]

class AdminCheckCheck(MsgModel):
    """text.format: username month_count"""
    text: str = """
Пользователь <b>@{username}</b> отправил чек и ожидает подтверждения оплаты
Срок подписки: <b>{month_count}</b> месяцев

Вы подтверждаете оплату?
    """

class MySubscribeActive(MsgModel):
    """text.format: residue username"""

    text: str = """
Статус подписки: активна
Период подписки: {residue} дней

Профиль Телеграм @{username}
    """

    markup: List[List[IButton]] = [
        [IButton(text='Тех. поддержка', callback_data='support')],
        [IButton(text='Назад', callback_data='to_start')]
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'my_subscribe'

class MySubscribeInactive(MsgModel):
    text: str = """
Ваша подписка: не активна
    """

    markup: List[List[IButton]] = [
        [IButton(text='Получить доступ', callback_data='get_access')],
        [IButton(text='Тех. поддержка', callback_data='support')],
        [IButton(text='Реферальная система', callback_data='referral')],
        [IButton(text='Назад', callback_data='to_start')]
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'my_subscribe'

class Support(MsgModel):
    text: str = """
Если возникли вопросы, смело пишите нам:

Официальный аккаунт
@atrums_manager
    """

    markup: List[List[IButton]] = [
        [IButton(text='Назад', callback_data='to_start')]
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'support'

class Referral(MsgModel):
    """text.format: balance referral_count referral_url"""

    text: str = """
Вы можете приглашать друзей с помощью своей реферальной ссылки и получать вознаграждение. За каждого привлечённого пользователя в закрытое сообщество ATRUMS вам начисляется 10% от его покупки.

Ваш текущий реферальный баланс составляет: {balance}$

По вашей ссылке перешли: {referral_count} человек

Ваша реферальная ссылка:
<b><code>{referral_url}</code></b>

Вывод реферального баланса доступен с 20$.

<blockquote expandable>Рефералы:{referrals}</blockquote>
    """

    markup: List[List[IButton]] = [
        [IButton(text='Назад', callback_data='to_start')]
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'referral'

class MoreInfo(MsgModel):
    text: str = """
Мы пришли на рынок криптовалют, чтобы зарабатывать, поэтому охватываем практически все направления, где можно получить результат как в моменте, так и чуть подольше

<b>Что вы получите?</b>
🟣 <i>Сильное окружение</i>
🟣 <i>Рабочие стратегии</i>
🟣 <i>Моментальные ответы на вопросы</i>
🟣 <i>Различные схемки</i>
🟣 <i>Результаты</i>

Открыт к новым возможностям? Жми на кнопку и присоединяйся к нам! 
<b>"ХОЧУ ПОПАСТЬ"</b>
    """

    markup: List[List[IButton]] = [
        [IButton(text='ХОЧУ ПОПАСТЬ', callback_data='get_access')],
        [IButton(text='Назад', callback_data='to_start')]
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'what_in_closed'

class Pass(MsgModel):
    text: str = """

    """

    markup: List[List[IButton]] = [
        [IButton(text='Назад', callback_data='to_start')]
    ]
