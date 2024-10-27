from datetime import datetime
from typing import Literal, List

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Annotated

from db import Base

lit_role = Literal['user']
lit_currency = Literal['rub', 'usdt']
lit_pay_method = Literal['bank_money', 'crypto']

id_pk = Annotated[int, mapped_column(primary_key=True)]
now_dtime = Annotated[datetime, mapped_column(default=func.now())]

class UserTable(Base):
    __tablename__ = 'usertable'
    id: Mapped[id_pk]
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str|None]
    first_name: Mapped[str|None]
    created_at: Mapped[now_dtime]
    role: Mapped[lit_role] = mapped_column(default='user')
    next_msg_info: Mapped[str|None] = mapped_column(default=None)
    balance: Mapped[float] = mapped_column(default=0.0)
    referral_id: Mapped[int] = mapped_column(ForeignKey('usertable.id'), default=None, nullable=True)


    self_child = relationship('UserTable')
    payment: Mapped[List['Payment']] = relationship()
    UserMessage: Mapped[List['UserMessage']] = relationship()
    def __str__(self):
        return f'USER: id={self.id}, username={self.username or "NULL"}, role={self.role}'

class Payment(Base):
    __tablename__ = 'payment'
    id: Mapped[id_pk]
    usertable_id: Mapped[int] = mapped_column(ForeignKey('usertable.id'))
    bought_at: Mapped[now_dtime]
    will_end_at: Mapped[datetime]
    duration_in_month: Mapped[int]
    payment_method: Mapped[lit_pay_method]
    transaction_hash: Mapped[str|None]
    check_file_id: Mapped[str|None]
    currency: Mapped[lit_currency]
    price: Mapped[float]

    # usertable: Mapped['UserTable'] = relationship(back_populates='payment')

    def __str__(self):
        return f'ID: {self.id}, USER: id={self.usertable_id}, PRICE: {self.price} {self.currency}'

class UserMessage(Base):
    __tablename__ = 'usermessage'
    id: Mapped[id_pk]
    usertable_id: Mapped[int] = mapped_column(ForeignKey('usertable.id'))
    type: Mapped[str]
    text: Mapped[str|None]
    file_id: Mapped[str|None]
    send_at: Mapped[datetime]
    message_id: Mapped[int]

    # usertable: Mapped['UserTable'] = relationship(back_populates='usermessage')

    def __str__(self):
        return f'ID: {self.id}, USER: id={self.usertable_id}, TYPE: {self.type}, TEXT: {self.text}'

class BotMessage(Base):
    __tablename__ = 'botmessage'
    id: Mapped[id_pk]
    type: Mapped[str]
    text: Mapped[str | None]
    file_id: Mapped[str | None]
    send_at: Mapped[datetime]
    message_id: Mapped[int]

    def __str__(self):
        return f'ID: {self.id}, TYPE: {self.type}, TEXT: {self.text}'

