from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedInstanceError
from models import Test


engine = create_engine("sqlite:///app.sqlite3")
Session = sessionmaker(engine)
session = Session()

def add_data():
    test = Test(name="qiitaro",age=26)
    session.add(test)
    session.commit()

def select_all():
    tests = session.query(Test).all()
    for test in tests:
        print(test.id,test.name,test.age)
    session.close()
# to
def update():
    pass

# idで指定して削除
def delete_one(id):
    try:
        test = session.query(Test).get(id)
        session.delete(test)
        session.commit()
        print(f"id:{test.id} 名前:{test.name} 年齢:{test.age}を削除しました")

    except UnmappedInstanceError:
        session.rollback()
        print(f"{id}は存在しません")


# idで最小の1つを動的に削除
from sqlalchemy.sql import func
def delete_minimum_one():
    try:
        q = session.query(func.min(Test.id).label("min_id")).one()
        test = session.query(Test).get(q.min_id)
        session.delete(test.id)
        session.commit()
        print(f"id:{test.id} 名前:{test.name} 年齢:{test.age}を削除しました")

    except UnmappedInstanceError:
        session.rollback()
        print(f"{id}は存在しません")

add_data()
# delete_one(21)
delete_minimum_one()
select_all()
