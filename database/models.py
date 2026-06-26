from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='documents')

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Float, nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    document = relationship('Document', back_populates='chunks')

class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    user = relationship('User', back_populates='chat_sessions')
    document = relationship('Document', back_populates='chat_sessions')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    chunk_ids = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    session = relationship('ChatSession', back_populates='messages')

User.documents = relationship('Document', order_by=Document.id, back_populates='user')
User.chat_sessions = relationship('ChatSession', order_by=ChatSession.id, back_populates='user')
Document.chunks = relationship('DocumentChunk', order_by=DocumentChunk.id, back_populates='document')
Document.chat_sessions = relationship('ChatSession', order_by=ChatSession.id, back_populates='document')
ChatSession.messages = relationship('ChatMessage', order_by=ChatMessage.id, back_populates='session')