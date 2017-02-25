""" Models for SQLAlchemy ORM """
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(
    'postgresql://black:black101@localhost/black', 
    echo=True)

Session_builder = sessionmaker(bind=engine)

sessions = list()

def get_new_session():
    session = Session_builder()
    sessions.append(session)

    return session

def destroy_session(session):
    sessions_by_class = filter(lambda x: x == session, sessions)

    for session in sessions_by_class:
        session.close()
        sessions.remove(session)

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    project_name = Column(String, primary_key=True)

    def __repr__(self):
       return "<Project(project_name='%s'>" % (
                            self.project_name)


class Task(Base):
    __tablename__ = 'tasks'
    task_id = Column(String, primary_key=True)
    task_type = Column(String)
    target = Column(String)
    params = Column(String)
    status = Column(String)
    project_name = Column(String, ForeignKey('projects.project_name'))

    # def __repr__(self):
    #    return "<Task(task_id='%s', task_type='%s',)>" % (
    #                         self.project_name)


class Scope(Base):
    __tablename__ = 'scopes'
    scope_id = Column(String, primary_key=True)
    hostname = Column(String)
    ip_address = Column(String)
    project_name = Column(String, ForeignKey('projects.project_name'))

    def __repr__(self):
       return """<Scope(scope_id='%s', hostname='%s',
                        ip_address='%s', project_name='%s')>""" % (
                        self.scope_id, self.hostname,
                        self.ip_address, self.project_name)


class Scan(Base):
    __tablename__ = 'scans'
    id = Column(String, primary_key=True)
    target = Column(String)
    port_number = Column(Integer)
    protocol = Column(String)
    banner = Column(String)
    screenshot_path = Column(String)
    task_id = Column(String, ForeignKey('tasks.task_id')) # TODO: add on_delete
    project_name = Column(String, ForeignKey('projects.project_name'))

    # def __repr__(self):
    #    return "<Scan(project_name='%s'>" % (
    #                         self.project_name)


session = get_new_session()
Base.metadata.create_all(engine, checkfirst=True)
destroy_session(session)
