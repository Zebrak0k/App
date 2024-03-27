import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Укажите путь к базе данных")

    connect_str = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f'Подключение к базе данных по адресу {db_file}')

    engine = sa.create_engine(connect_str, echo=True)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


