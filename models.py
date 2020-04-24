from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

#I have all of my tables in here
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer,primary_key=True)
    color = Column(String)
    name = Column(String)

    def __repr__(self):
        return "{} is a {}".format(self.name,self.color)

class BookRead(Base):
    __tablename__ = 'bookreading'
    id = Column(Integer,primary_key=True)
    title = Column(String)
    description = Column(String)
    purchaseInfo = Column(String)
    currBook = Column(Boolean)

    def __repr__(self):
        return "Title: {} \nDescription: {} \nPurchase Information: {}".format(self.title,self.description,self.purchaseInfo)

class BookList(Base):
    __tablename__ = 'booklist'
    id = Column(Integer,primary_key=True)
    title = Column(String)
    description = Column(String)

    def __repr__(self):
        return "Title: {}\nDescription: {}".format(self.title,self.description)
