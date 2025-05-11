import re
import sqlalchemy as db
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm.exc import NoResultFound

def create_contact(arg, session):
    try:
        if (re.search(r'^\+\d[\d\(\)-]{2,20}$', arg[2])):
            exist = session.query(Contact).filter(db.or_(Contact.name == arg[1].lower(), Contact.number == arg[2])).one()
            print("Похожий контакт уже существует: ", exist.name, exist.number)
        else:
            print("Номер указан неверно.")
    except NoResultFound:
        new_contact = Contact(name=arg[1].lower(), number=arg[2])
        session.add(new_contact)
        session.commit()
        session.refresh(new_contact)
        print("Контакт добавлен с id: ", new_contact.id)
    except IndexError:
        print("Параметры команды введены неверно.")

def delete_contact(arg, session):
    try:
        contact = session.query(Contact).filter(Contact.name==arg[1].lower()).first()
        if contact:
            session.delete(contact)
            session.commit()
            print("Контакт ", arg[1], " удалён.")
        else:
            print("Контакт с именем ", arg[1], " не найден.")
    except IndexError:
        print("Параметры команды введены неверно.")

def print_contact(arg, session):
    try:
        contact = session.query(Contact).filter(Contact.name == arg[1].lower()).first()
        if contact:
            print(contact.id, ": ", contact.name, " ", contact.number)
        else:
            print("Контакт с именем ", arg[1], " не найден.")
    except IndexError:
        print("Параметры команды введены неверно.")

def print_phone_book(session):
    for contact in session.query(Contact).all():
        print(contact.id, ": ", contact.name, " ", contact.number)


menu = {
    "add": create_contact,
    "del": delete_contact,
    "list": print_contact,
    "list_all": print_phone_book
    }

#ПОДГОТОВКА К СЕССИИ
engine = db.create_engine('sqlite:///Phones.db')  #echo=True

class Base(DeclarativeBase): pass

class Contact(Base):
    __tablename__ = "phonebook"
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    number = db.Column(db.String(18), unique=True, nullable=False)

#создание таблиц
Base.metadata.create_all(bind=engine)

#НАЧАЛО СЕССИИ
with Session(autoflush=False, bind=engine) as session:
    print("""Список команд для управления контактами:
                    add <имя_контакта> <номер_телефона> - добавление контакта
                    del <имя_контакта> - удаление контакта
                    list <имя_контакта> - вывести информацию о контакте
                    list (без аргументов) - вывести список всех контактов
                    exit - закончить работу""")
    while True:
        command = input("\n Введите команду: ")
        arg = command.split(" ")

        if arg[0] in menu:
            if (arg[0] == "list" and len(arg) == 1):
                menu["list_all"](session)
            else:
                menu[arg[0]](arg, session)
        elif arg[0] == "exit":
            break
        else:
            print("Команды ", arg[0], " нет в списке.")

