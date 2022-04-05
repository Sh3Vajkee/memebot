from sqlalchemy import Column, Integer, BigInteger, String, Text

from db.base import Base


class Lobby(Base):
    __tablename__ = 'lobby'

    msg_id = Column(BigInteger, primary_key=True,
                    unique=True, autoincrement=False)
    msg_text = Column(Text)
    owner_id = Column(BigInteger, unique=True, autoincrement=False)
    owner_username = Column(String(100))
    total_players = Column(Integer, default=1)
    ready_players = Column(Integer, default=0)
    round = Column(Integer, default=0)
    phrase_link = Column(String(255))
    phrase_text = Column(String(255))
    status = Column(String(10), default='Open')


class CurrentPlayers(Base):
    __tablename__ = 'currentplayers'

    player_id = Column(BigInteger, primary_key=True,
                       unique=True, autoincrement=False)
    user_name = Column(String(100))
    lobby_id = Column(BigInteger, autoincrement=False)
    pic_id = Column(Integer)
    likes = Column(Integer, default=0)
    ready = Column(String(10), default='No')
    liked = Column(String(10), default='No')


class MemeImages(Base):
    __tablename__ = 'memeimages'

    img_id = Column(Integer, primary_key=True,
                    unique=True, autoincrement=False)
    link = Column(String(255))


class MemeRound(Base):
    __tablename__ = 'memeround'

    lobby_id = Column(BigInteger, autoincrement=False)
    player_id = Column(BigInteger, primary_key=True, autoincrement=False)
    img_link = Column(String(255))


class PhraseImages(Base):
    __tablename__ = 'phraseimages'

    phrase_id = Column(Integer, primary_key=True,
                       unique=True, autoincrement=False)
    link = Column(String(255))
    text = Column(String(255))


class PhraseRound(Base):
    __tablename__ = 'phraseround'

    lobby_id = Column(BigInteger, autoincrement=False)
    phrase_id = Column(Integer, primary_key=True, autoincrement=False)
    link = Column(String(255))
    text = Column(String(255))

    def __repr__(self) -> str:
        return f'{self.lobby_id} - {self.phrase_id}'


class MsgLike(Base):
    __tablename__ = 'msglike'

    lobby_id = Column(BigInteger, autoincrement=False)
    msg_id = Column(BigInteger, autoincrement=False, primary_key=True)
    chat_id = Column(BigInteger, autoincrement=False)

class MsgChoice(Base):
    __tablename__ = 'msgchoice'

    lobby_id = Column(BigInteger, autoincrement=False)
    msg_id = Column(BigInteger, autoincrement=False, primary_key=True)
    chat_id = Column(BigInteger, autoincrement=False)
