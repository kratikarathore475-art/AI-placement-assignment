from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models.user import User
from models.question import Question, ProgressEntry
from models.interview import Interview, InterviewTurn

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, name: str, email: str, password: str) -> User:
    hashed = pwd_context.hash(password)
    user = User(name=name, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def bulk_insert_questions(db: Session, questions: list) -> int:
    inserted = 0
    for q in questions:
        exists = db.query(Question).filter(Question.external_id == q["id"]).first()
        if exists:
            continue
        db_question = Question(
            external_id=q["id"],
            topic=q["topic"],
            question_text=q["question"],
            answer_text=q["answer"],
        )
        db.add(db_question)
        inserted += 1
    db.commit()
    return inserted


def get_questions_by_topic(db: Session, topic: str, limit: int = 20):
    return db.query(Question).filter(Question.topic == topic).limit(limit).all()


def log_progress(db: Session, user_id: int, question_id: int,
                  user_answer: str, was_correct: bool = None) -> ProgressEntry:
    entry = ProgressEntry(user_id=user_id, question_id=question_id,
                           user_answer=user_answer, was_correct=was_correct)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_user_progress_summary(db: Session, user_id: int) -> dict:
    entries = db.query(ProgressEntry).filter(ProgressEntry.user_id == user_id).all()
    total = len(entries)
    correct = sum(1 for e in entries if e.was_correct)
    return {"total_attempted": total, "correct": correct,
            "accuracy": round(correct / total, 2) if total else 0.0}


def create_interview(db: Session, user_id: int, topic_focus: str = None) -> Interview:
    interview = Interview(user_id=user_id, topic_focus=topic_focus)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def add_interview_turn(db: Session, interview_id: int, turn_number: int,
                        question_text: str, user_answer: str = None,
                        feedback: str = None, score: float = None) -> InterviewTurn:
    turn = InterviewTurn(interview_id=interview_id, turn_number=turn_number,
                          question_text=question_text, user_answer=user_answer,
                          feedback=feedback, score=score)
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn