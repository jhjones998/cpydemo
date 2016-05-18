from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from cherrypy import Tool, request, engine
from cherrypy.process import plugins


from sqlalchemy_orm import Base


class SAEnginePlugin(plugins.SimplePlugin):
    def __init__(self, bus, connection_string):
        super(SAEnginePlugin, self).__init__(bus)
        self.sa_engine = None
        self.conn_string = connection_string
        self.bus.subscribe("bind", self.bind)

    def start(self):
        self.sa_engine = create_engine(self.conn_string, echo=True)
        Base.metadata.create_all(self.sa_engine)

    def stop(self):
        if self.sa_engine:
            self.sa_engine.dispose()
            self.sa_engine = None

    def bind(self, session):
        session.configure(bind=self.sa_engine)


class SATool(Tool):
    def __init__(self):
        super(SATool, self).__init__(
            'on_start_resource', self.bind_session, priority=20
        )

        self.session = scoped_session(
            sessionmaker(
                autoflush=True, autocommit=False
            )
        )

    def _setup(self):
        super(SATool, self)._setup()
        request.hooks.attach(
            'on_end_resource',
            self.commit_transaction,
            priority=80
        )

    def bind_session(self):
        engine.publish('bind', self.session)
        request.db = self.session

    def commit_transaction(self):
        request.db = None
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.remove()
