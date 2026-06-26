import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import (
    SessionLocal,
    User,
    Document,
    DocumentChunk,
    ChatSession,
    ChatMessage
)

def seed_database():
    session = SessionLocal()
    try:
        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="user1@example.com",
            hashed_password="hashed_password_1",
            created_at=None,
            updated_at=None
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="user2@example.com",
            hashed_password="hashed_password_2",
            created_at=None,
            updated_at=None
        )
        user3 = User(
            id=str(uuid.uuid4()),
            email="user3@example.com",
            hashed_password="hashed_password_3",
            created_at=None,
            updated_at=None
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            filename="document1.txt",
            file_path="/path/to/document1.txt",
            file_size=1024,
            status="processed",
            created_at=None,
            processed_at=None
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            filename="document2.txt",
            file_path="/path/to/document2.txt",
            file_size=2048,
            status="processed",
            created_at=None,
            processed_at=None
        )
        document3 = Document(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            filename="document3.txt",
            file_path="/path/to/document3.txt",
            file_size=4096,
            status="processing",
            created_at=None,
            processed_at=None
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=0,
            content="This is the first chunk of document1.",
            embedding=[0.1] * 1536,
            metadata=None,
            created_at=None
        )
        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document2.id,
            chunk_index=0,
            content="This is the first chunk of document2.",
            embedding=[0.2] * 1536,
            metadata=None,
            created_at=None
        )
        chunk3 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document3.id,
            chunk_index=0,
            content="This is the first chunk of document3.",
            embedding=[0.3] * 1536,
            metadata=None,
            created_at=None
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed ChatSessions
        chat_session1 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            document_id=document1.id,
            title="Chat about document1",
            created_at=None,
            updated_at=None
        )
        chat_session2 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            document_id=document2.id,
            title="Chat about document2",
            created_at=None,
            updated_at=None
        )
        chat_session3 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            document_id=document3.id,
            title="Chat about document3",
            created_at=None,
            updated_at=None
        )
        session.add_all([chat_session1, chat_session2, chat_session3])
        session.commit()

        # Seed ChatMessages
        message1 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=chat_session1.id,
            role="user",
            content="What is this document about?",
            chunk_ids=[chunk1.id],
            created_at=None
        )
        message2 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=chat_session2.id,
            role="assistant",
            content="This document is about AI.",
            chunk_ids=[chunk2.id],
            created_at=None
        )
        message3 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=chat_session3.id,
            role="system",
            content="Processing document3.",
            chunk_ids=[chunk3.id],
            created_at=None
        )
        session.add_all([message1, message2, message3])
        session.commit()

        print("Database seeded successfully!")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()