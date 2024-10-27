import asyncio
import datetime
import json
import re
import traceback
from datetime import timezone
from typing import Union, Literal, List

import aiogram
import httpx
from aiogram import Bot, Dispatcher, types as tg_types, F, exceptions
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Filter
from aiogram.types import InlineKeyboardButton as IButton, InlineKeyboardMarkup, FSInputFile, Message, CallbackQuery

from core import UserCore, UserMessageCore, BotMessageCore, PaymentCore
import messages
from messages import MsgModel, config

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher()

async def check_users():
    while True:
        try:
            await asyncio.sleep(8*60*60)
            today = datetime.datetime.now()

            all_subscribes = await PaymentCore.find_all()
            for subscribe in all_subscribes:
                if subscribe.will_end_at < today:
                    await asyncio.sleep(61)
                    user = await UserCore.find_one(id=subscribe.usertable_id)
                    for chat_id in config.CHATS_FOLDER_IDS:
                        await bot.ban_chat_member(
                            chat_id=chat_id,
                            user_id=user.id
                        )
                    await PaymentCore.delete(id=subscribe.id)
        except Exception as err:
            traceback.print_exc()

async def send_message(model: messages.MsgModel) -> Message:
    if not model.photo:
        sent =  await bot.send_message(
            chat_id=model.id,
            text=model.text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=model.markup) if model.markup else model.markup,
            reply_to_message_id=model.reply_to_message_id,
            disable_notification=model.disable_notifications,
            disable_web_page_preview=model.disable_web_page_preview,
            parse_mode=model.parse_mode
        )
        await BotMessageCore.add(
            type='text',
            text=model.text,
            send_at=sent.date,
            message_id=sent.message_id
        )
        return sent
    else:
        sent = await bot.send_photo(
            chat_id=model.id,
            caption=model.text,
            photo=model.photo if model.photo_type == 'file_id' else FSInputFile(model.photo),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=model.markup) if model.markup else model.markup,
            reply_to_message_id=model.reply_to_message_id,
            disable_notification=model.disable_notifications,
            parse_mode=model.parse_mode
        )
        await BotMessageCore.add(
            type='text',
            text=model.text,
            file_id=sent.photo[-1].file_id,
            send_at=sent.date,
            message_id=sent.message_id
        )
        return sent

async def delete_message(model: MsgModel) -> None:
    try:
        await bot.delete_message(chat_id=model.id, message_id=model.message_id)
    except aiogram.exceptions.TelegramBadRequest:
        pass

async def update_message(model: messages.MsgModel) -> None:
    try:
        await bot.edit_message_text(
            chat_id=model.id,
            text=model.text,
            message_id=model.message_id,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=model.markup) if model.markup else model.markup,
            disable_web_page_preview=model.disable_web_page_preview,
            parse_mode=model.parse_mode
        )
    except aiogram.exceptions.TelegramBadRequest:
        try:
            await delete_message(model)
        except aiogram.exceptions.TelegramBadRequest:
            pass
        await send_message(model)

async def save_user_message(message: Message, user_pk: int):
    content_type = message.content_type
    text = message.text or message.caption
    file_id = None
    if content_type == 'photo':
        file_id = message.photo[-1].file_id

    await UserMessageCore.add(
        usertable_id=user_pk,
        type=content_type,
        text=text,
        file_id=file_id,
        send_at=message.date,
        message_id=message.message_id
    )


class MsgTypeF(Filter):
    message_type = None

    def __init__(self, message_type: Literal['photo', 'text'] = None):
        """
        Check private or not
        and message content type photo or text
        :param message_type:
        """
        self.message_type = message_type

    async def __call__(self, update: Message, *args, **kwargs):
        check_message_type = update.content_type == self.message_type

        return check_message_type


class PrivateF(Filter):
    async def __call__(self, update: Union[Message, tg_types.CallbackQuery], *args, **kwargs):
        if type(update) == Message:
            chat = update.chat
        else:
            chat = update.message.chat

        return chat.type == 'private'


class ReFullmatchF(Filter):
    pattern = None
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    async def __call__(self, callback: CallbackQuery, *args, **kwargs):
        rres = re.fullmatch(self.pattern, callback.data)
        if rres:
            return True
        else:
            return False


class NextMsgInfoCheckF(Filter):
    async def __call__(self, update: Message, *args, **kwargs):
        res = await UserCore.find_one(user_id=update.from_user.id)
        if res:
            next_msg_info = res.next_msg_info

            comparison_dict = {
                'rubles': 'photo',
                'crypto': 'text',
            }

            if update.text:
                with open('config.json') as read_f:
                    data = json.load(read_f)
                if data['enable_promo'] is True:
                    if update.text.upper().strip() in ('ATRUMS30', 'ATRUMS50'):
                        comparison_dict = {
                            'rubles': 'text',
                            'crypto': 'text',
                        }

            if next_msg_info:
                return comparison_dict[next_msg_info.split('/')[0]] == update.content_type
        else:
            return False

# next_message
@dp.message(PrivateF(), MsgTypeF('text'), NextMsgInfoCheckF())
async def start_update(message: Message):
    user = message.from_user
    text = message.text

    db_user = await UserCore.find_one(user_id=user.id)
    next_msg_info_split = db_user.next_msg_info.split('/')
    with open('config.json') as read_f:
        data = json.load(read_f)
    if data['enable_promo'] is True:
        if text.upper().strip() in ('ATRUMS30', 'ATRUMS50'):
            if next_msg_info_split[1].count(',') == 0:
                month_count = next_msg_info_split[1] + (',0.3' if text.upper().strip() == 'ATRUMS30' else ',0.5')
            else:
                month_count = next_msg_info_split[1]
            await UserCore.update(filter_by={'user_id': user.id}, next_msg_info=f'{next_msg_info_split[0]}/{month_count}/{message.message_id}')
            if next_msg_info_split[0] == 'crypto':
                pay_amount_dict = {
                    '3': '300',
                    '6': '550',
                    '12': '900',
                    '3,0.3': '210',
                    '3,0.5': '150',
                    '6,0.3': '385',
                    '6,0.5': '275',
                    '12,0.3': '630',
                    '12,0.5': '450',
                }
    
                msg = messages.PayAccessCrypto(id=user.id, message_id=message.message_id)
                msg.text = msg.text.format(day_count=str(int(month_count.split(',')[0]) * 30), pay_amount=pay_amount_dict[month_count])
                await update_message(msg)
    
            else:
                pay_amount_dict = {
                    '3': '30.000',
                    '6': '55.000',
                    '12': '90.000',
                    '3,0.3': '21 000',
                    '3,0.5': '15 000',
                    '6,0.3': '38 500',
                    '6,0.5': '27 500',
                    '12,0.3': '63 000',
                    '12,0.5': '45 000',
                }
    
                msg = messages.PayAccessRubles(id=user.id, message_id=message.message_id)
                msg.text = msg.text.format(day_count=str(int(month_count.split(',')[0]) * 30), pay_amount=pay_amount_dict[month_count])
                await update_message(msg)
            return
    
    count_month = next_msg_info_split[1]
    month_to_amount = {
        '3': 300,
        '6': 550,
        '12': 900,
        '3,0.3': 210,
        '3,0.5': 150,
        '6,0.3': 385,
        '6,0.5': 275,
        '12,0.3': 630,
        '12,0.5': 450,
    }
    right_amount = month_to_amount[count_month]

    async def send_error():
        await delete_message(MsgModel(id=user.id, message_id=int(db_user.next_msg_info.split('/')[2])))
        await send_message(messages.PayError(id=user.id))
        await UserCore.update(filter_by={'user_id': user.id}, next_msg_info=None)

    async with httpx.AsyncClient() as client:
        response = await client.get('https://apilist.tronscanapi.com/api/transaction-info', params={'hash': text.strip()})
        json_req = response.json()

    if json_req == {}:
        return await send_error()

    contract_ret = json_req['contractRet']
    if contract_ret != 'SUCCESS':
        return await send_error()

    confirmed = json_req['confirmed']
    if not confirmed is True:
        return await send_error()

    to_address = json_req['toAddress']
    if to_address != config.TO_ADDRESS:
        return await send_error()

    amount = json_req['trc20TransferInfo']['amount_str'] / 1000000
    if amount != right_amount:
        return await send_error()

    await delete_message(MsgModel(id=user.id, message_id=int(db_user.next_msg_info.split('/')[2])))

    markup = []

    for i in config.CHATS_FOLDER_IDS:
        res = await bot.create_chat_invite_link(chat_id=i, member_limit=1)
        res2 = await bot.get_chat(chat_id=i)
        markup.append([IButton(text=res2.first_name, url=res.invite_link)])

    msg = messages.PaySuccess(id=user.id)
    msg.markup = markup
    await send_message(msg)

    will_end_at = datetime.datetime.utcnow() + datetime.timedelta(days=30*int(count_month))
    await PaymentCore.add(
        usertable_id=db_user.id,
        will_end_at=will_end_at,
        duration_in_month=int(count_month),
        payment_method='crypto',
        transaction_hash=text,
        currency='usdt',
        price=right_amount
    )

    await UserCore.update(filter_by={'user_id': user.id}, next_msg_info=None)

# next_message
@dp.message(PrivateF(), MsgTypeF('photo'), NextMsgInfoCheckF())
async def start_update(message: Message):
    user = message.from_user

    db_user = await UserCore.find_one(user_id=user.id)

    count_month = db_user.next_msg_info.split('/')[1]
    sent_message_id = db_user.next_msg_info.split('/')[2]

    await delete_message(MsgModel(id=user.id, message_id=sent_message_id))

    msg_to_user = messages.RublesAfterPayInfo(id=user.id)
    await send_message(msg_to_user)

    await bot.forward_message(config.ADMIN_ID, user.id, message.message_id)
    msg_to_admin = messages.AdminCheckCheck(id=config.ADMIN_ID)
    msg_to_admin.text = msg_to_admin.text.format(username=user.username or 'username', month_count=count_month)
    msg_to_admin.markup = [[
        IButton(text='Да', callback_data=f'{db_user.id}/{count_month}/yes'),
        IButton(text='Нет', callback_data=f'{db_user.id}/{count_month}/no'),
    ]]
    await send_message(msg_to_admin)

    await UserCore.update(filter_by={'user_id': user.id}, next_msg_info=None)

# команда /start
@dp.message(PrivateF(), MsgTypeF('text'), F.text[:6] == '/start')
async def start_update(message: Message):
    user = message.from_user
    text = message.text

    db_user = await UserCore.find_one(user_id=user.id)
    if not db_user:
        referral_id = None
        rres = re.fullmatch(r'/start ([0-9-]+)', text)
        if rres:
            referral_id = int(rres.group(1))

        await UserCore.add(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            referral_id=referral_id
        )
    db_user = await UserCore.find_one(user_id=user.id)

    await save_user_message(message, db_user.id)

    msg = messages.StartMessage(id=user.id)
    msg.text = msg.text.format(first_name=user.first_name or user.username)
    await send_message(msg)

@dp.message(PrivateF(), MsgTypeF('text'), F.text[:6] == '/promo')
async def promo(message: Message):
    with open('config.json') as read_f:
        data = json.load(read_f)
    
    enable_promo = False if data['enable_promo'] is True else True
    
    with open('config.json', 'w') as write_f:
        json.dump({'enable_promo': enable_promo}, write_f)
    
    await send_message(MsgModel(id=message.from_user.id, text='Промокоды выключены' if enable_promo is False else 'Промокоды включены'))
    
# кнопка (отмена)
@dp.callback_query(PrivateF(), F.data == 'to_start')
async def to_start(callback: CallbackQuery):
    user = callback.from_user
    message = callback.message
    msg = messages.StartMessage(
        id=user.id,
        message_id=message.message_id
    )

    msg.text = msg.text.format(first_name=user.first_name or user.username)

    await update_message(msg)

    await UserCore.update(filter_by={'user_id': user.id}, next_msg_info=None)

# кнопка (получить доступ)
@dp.callback_query(PrivateF(), F.data == 'get_access')
async def get_access1(callback: CallbackQuery):
    msg = messages.GetAccess(
        id=callback.from_user.id,
        message_id=callback.message.message_id
    )

    await update_message(msg)

# кнопка выбора месяцев подписки
@dp.callback_query(PrivateF(), ReFullmatchF('get_access/(3|6|12)_month'))
async def get_access2(callback: CallbackQuery):
    cdata = callback.data
    user = callback.from_user
    message = callback.message
    rres = re.fullmatch(r'get_access/(3|6|12)_month', cdata)
    month_count = rres.group(1)

    msg = messages.GetAccessXMonth(
        id=user.id,
        message_id=message.message_id,
        markup=[
            [IButton(text='Криптовалюта', callback_data=f'get_access/{month_count}_month/crypto')],
            [IButton(text='Рубли', callback_data=f'get_access/{month_count}_month/rubles')]
        ]
    )

    await update_message(msg)

# кнопка выбора метода оплаты
@dp.callback_query(PrivateF(), ReFullmatchF('get_access/(3|6|12)(,0.3|.0.5|)_month/(crypto|rubles)'))
async def get_access3(callback: CallbackQuery):
    cdata = callback.data
    user = callback.from_user
    message = callback.message

    rres = re.fullmatch(r'get_access/(3|6|12)(|,0.3|.0.5)_month/(crypto|rubles)', cdata)
    month_count = rres.group(1) + rres.group(2)
    pay_type = rres.group(3)

    if pay_type == 'crypto':
        pay_amount_dict = {
            '3': '300',
            '6': '550',
            '12': '900',
            '3,0.3': '210',
            '3,0.5': '150',
            '6,0.3': '385',
            '6,0.5': '275',
            '12,0.3': '630',
            '12,0.5': '450',
        }

        msg = messages.PayAccessCrypto(id=user.id, message_id=message.message_id)
        msg.text = msg.text.format(day_count=str(int(month_count) * 30), pay_amount=pay_amount_dict[month_count])
        await update_message(msg)

    elif pay_type == 'rubles':
        pay_amount_dict = {
            '3': '30.000',
            '6': '55.000',
            '12': '90.000'
        }

        msg = messages.PayAccessRubles(id=user.id, message_id=message.message_id)
        msg.text = msg.text.format(day_count=str(int(month_count) * 30), pay_amount=pay_amount_dict[month_count])
        await update_message(msg)

    await UserCore.update(filter_by={'user_id': user.id}, next_msg_info=f'{pay_type}/{month_count}/{message.message_id}')

@dp.callback_query(PrivateF(), ReFullmatchF('[0-9]+/(3|6|12)(,0.3|,0.5|)/(yes|no)'))
async def yes_no(callback: CallbackQuery):
    cdata = callback.data
    user = callback.from_user
    message = callback.message

    rres = re.fullmatch(r'([0-9]+)/(3|6|12)(,0.3|.0.5|)/(yes|no)', cdata)
    db_user_id = int(rres.group(1))
    month_count = rres.group(2)
    answer = rres.group(4)

    db_user = await UserCore.find_one(id=db_user_id)

    if answer == 'yes':
        markup = []
        for i in config.CHATS_FOLDER_IDS:
            res = await bot.create_chat_invite_link(chat_id=i, member_limit=1)
            res2 = await bot.get_chat(chat_id=i)
            markup.append([IButton(text=res2.title, url=res.invite_link)])

        msg = messages.PaySuccess(id=db_user.user_id)
        msg.markup = markup
        await send_message(msg)

        will_end_at = datetime.datetime.utcnow() + datetime.timedelta(days=30 * int(month_count))
        month_to_amount = {
            '3': 30000,
            '6': 55000,
            '12': 90000,
            '3,0.3': 21000,
            '3,0.5': 15000,
            '6,0.3': 38500,
            '6,0.5': 27500,
            '12,0.3': 63000,
            '12,0.5': 45000,
        }
        right_amount = month_to_amount[month_count]
        await PaymentCore.add(
            usertable_id=db_user.id,
            will_end_at=will_end_at,
            duration_in_month=int(month_count),
            payment_method='bank_money',
            currency='usdt',
            price=right_amount
        )
    else:
        await send_message(messages.PayError(id=db_user.user_id))

    await delete_message(MsgModel(id=user.id, message_id=message.message_id))

@dp.callback_query(PrivateF(), F.data == 'my_subscribe')
async def my_subscribe(callback: CallbackQuery):
    user = callback.from_user
    db_user = await UserCore.find_one(user_id=user.id)
    subscribe = await PaymentCore.find_one(usertable_id=db_user.id)

    if subscribe:
        msg = messages.MySubscribeActive(id=user.id, message_id=callback.message.message_id)
        residue = str((subscribe.will_end_at - datetime.datetime.utcnow()).days)
        msg.text = msg.text.format(residue=residue, username=user.username or 'username')
        await update_message(msg)
    else:
        await update_message(messages.MySubscribeInactive(id=user.id, message_id=callback.message.message_id))

@dp.callback_query(PrivateF(), F.data == 'support')
async def support(callback: CallbackQuery):
    user = callback.from_user
    await update_message(messages.Support(id=user.id, message_id=callback.message.message_id))

@dp.callback_query(PrivateF(), F.data == 'referral')
async def referral(callback: CallbackQuery):
    user = callback.from_user
    db_user = await UserCore.find_one(user_id=user.id)
    referrals = await UserCore.find_all(referral_id=db_user.id)

    referral_count = str(len(referrals))
    referral_url = f'https://t.me/{config.BOT_USERNAME}?start={db_user.id}'
    list_referrals = ''
    for ref in referrals:
        if ref.username:
            list_referrals += '\n@' + ref.username
            if ref.first_name:
                list_referrals += '(' + ref.first_name + ')'
        elif ref.first_name:
            list_referrals += '\n' + ref.first_name
        else:
            list_referrals += '\nnoname'
    msg = messages.Referral(id=user.id, message_id=callback.message.message_id)
    msg.text = msg.text.format(balance=f'{db_user.balance:.2f}',
                               referral_count=referral_count,
                               referral_url=referral_url,
                               referrals=list_referrals[:3000])
    await update_message(msg)

@dp.callback_query(PrivateF(), F.data == 'more_info')
async def more_info(callback: CallbackQuery):
    user = callback.from_user
    await update_message(messages.MoreInfo(id=user.id, message_id=callback.message.message_id))

allowed_updates = ['message', 'callback_query']
async def start_polling():
    # noinspection PyAsyncCall
    await dp.start_polling(bot, polling_timeout=300, handle_signals=False, allowed_updates=allowed_updates)
