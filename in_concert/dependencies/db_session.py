from sqlalchemy.orm import sessionmaker


class DBSessionDependency:
    def __init__(self, engine):
        self.engine = engine
        self.session_factory: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def __call__(self) -> sessionmaker:
        try:
            session = self.session_factory()
            return session
        finally:
            session.close()
