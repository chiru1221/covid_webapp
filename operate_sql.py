# https://qiita.com/nagataaaas/items/5c7c9ec4813fea85c40c
# https://docs.sqlalchemy.org/en/13/core/type_basics.html
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
with open('db_name.txt', 'r', encoding='utf-8') as f:
    db_name = f.readline().strip()
ENGINE = create_engine('sqlite:///{0}.db'.format(db_name))
BASE = declarative_base()

class User(BASE):
    __tablename__ = 'user_action'
    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    day = Column(Date)
    name = Column(String)
    action = Column(String)

    def __repr__(self):
        return "User<{0}, {1}, {2}, {3}, {4}>".format(self.id, self.date, self.day, self.name, self.action)

class Temp(BASE):
    __tablename__ = 'user_temp'
    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    day = Column(Date)
    name = Column(String)
    temp = Column(Float)
    
    def __repr__(self):
        return "Temp<{0}, {1}, {2}, {3}, {4}>".format(self.id, self.date, self.day, self.name, self.temp)

class Ventil(BASE):
    __tablename__ = 'ventil_time'
    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime)
    day = Column(Date)
    ventil_s = Column(Time)
    ventil_e = Column(Time)

    def __repr__(self):
        return "Ventil<{0}, {1}, {2}, {3}, {4}>".format(self.id, self.date, self.day, self.ventil_s, self.ventil_e)

BASE.metadata.create_all(ENGINE)
SESSION_MAKER = sessionmaker(bind=ENGINE)
NAME_TO_TABLE = {
    'user_action': User,
    'user_temp': Temp,
    'ventil_time': Ventil,
}

def write_db(tablename, tableargs):
    try:
        session = SESSION_MAKER()
        record = NAME_TO_TABLE[tablename](**tableargs)
        session.add(record)
        session.commit()
        session.close()
    except:
        return 1
    return 0

def read_user_action(name, day):
    try:
        session = SESSION_MAKER()
        table = User
        action_list = list(map(lambda x: x[0], session.query(table.action).filter(table.name == name, table.day == day).all()))
        session.close()
        return action_list
    except:
        return None

def read_user_name(day):
    try:
        session = SESSION_MAKER()
        table = User
        in_list = list(map(lambda x: x[0], session.query(table.name).filter(table.day == day, table.action == '手洗い').all()))
        out_list = list(map(lambda x: x[0], session.query(table.name).filter(table.day == day, table.action == '帰宅').all()))
        session.close()
        return in_list, out_list
    except:
        return None, None

def read_ventilation_time(day):
    try:
        session = SESSION_MAKER()
        table = Ventil
        ventils = session.query(table.ventil_s, table.ventil_e).filter(table.day == day).all()
        session.close()
        return ventils
    except:
        return None

def del_ventilation_time(day):
    try:
        session = SESSION_MAKER()
        table = Ventil
        session.query(table).filter(table.day == day).delete()
        session.commit()
        session.close()
    except:
        return 1
    return 0


