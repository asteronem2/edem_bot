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
        [IButton(text='3 месяца (300$)', callback_data='get_access/3_month')],
        [IButton(text='6 месяца (550$)', callback_data='get_access/6_month')],
        [IButton(text='12 месяцев (900$)', callback_data='get_access/12_month')],
    ]
    photo_type: Literal['file_id', 'filename'] = 'file_id'
    photo_name: str | None = 'month_price'

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
(оплата только USDT, TRC20)

Нажми на кошелек, чтобы скопировать адрес кошелька.
Кошелёк: <blockquote><code>TFMMG1eRtyCzLXzPU2EywofXnm9hmXCkZV</code></blockquote>

После оплаты - отправьте хэш транзакции в чат.

Пример хэша — он содержится в транзакции, которую вы отправили. Если перевод был с биржи, найдите его в данных платежа.

Пример хэша: 5sse4105ae52ec3n2c0d9a372fe2a2ae3edde26jsaf5da72d9f17c9536c24ceb

<i>Если у вас есть <b>ПРОМОКОД</b>, сначала напишите его</i>

Скопируйте его и отправьте в бота👇
    """

    markup: List[List[IButton]] = [
        [IButton(text='Отмена', callback_data='to_start')],
    ]

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
Присоединяйся к закрытому сообществу экспертов в криптовалюте и получай доступ к ценнейшему опыту и уникальным инсайтам! 

Это не просто группа – это место, где профессионалы делятся своими знаниями, стратегиями и фишками. Мы разбираем самые перспективные направления в крипте, где за каждым направлением прикреплен специалист который делится своими действиями пошагово

Какие направления мы охватываем:
🔸 Процессинг 
🔸 P2P
🔸 Эйрдропы
🔸 NFT 
🔸 DeFi 
🔸 Откуп/Анализ монет 
🔸 Темки-Схемки (заработок в моменте, не только крипта)

Также вас ждут:
🔹 Еженедельные созвоны с кураторами по каждому направлению
🔹 Общий чат

Сообщество ATRUMS – твоя возможность всегда быть на шаг впереди остальных. Узнавай первым, действуй быстро и зарабатывай больше!

Открыт к новым возможностям? Жми на кнопку и присоединяйся к нам! 
"ХОЧУ ПОПАСТЬ"
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
