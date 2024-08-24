import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, insert


class DBConnection:
    __user = os.getenv('POSTGRES_USER')
    __password = os.getenv('POSTGRES_PASSWORD')
    __host = os.getenv('POSTGRES_HOST')
    __port = os.getenv('POSTGRES_PORT', '5432')
    __name = os.getenv('POSTGRES_DB')
    __con_str = f"postgresql+psycopg2://{__user}:{__password}@{__host}:{__port}/{__name}"
    __engine = create_engine(__con_str, echo=False,  client_encoding='utf8')

    def get_sites_metadata(self, table: str) -> list:
        meta_data = MetaData()
        table = Table(table, meta_data, autoload_with=self.__engine)
        Session = sessionmaker(self.__engine)

        with Session() as session:
            return session.query(table).all()

    def insert_table(self, table: str, insert_data: dict) -> None:
        meta_data = MetaData()
        table = Table('post', meta_data, autoload_with=self.__engine)

        Session = sessionmaker(self.__engine)

        with Session() as session:
            stmt = insert(table).values(insert_data)
            session.execute(stmt)
            session.commit()


if __name__ == '__main__':
    db = DBConnection()

    db.get_sites_metadata('register_sites')
