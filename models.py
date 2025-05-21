from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, event
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Specialty(Base):
    __tablename__ = 'specialties'
    __table_args__ = {'schema': 'university'}

    specialty_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    faculty = Column(String(100), nullable=False)
    seats_available = Column(Integer, nullable=False)
    study_form = Column(String(50), nullable=False)  # очная, заочная, очно-заочная
    tuition_fee = Column(Integer, nullable=False)  # стоимость обучения в рублях
    passing_score = Column(Integer)  # проходной балл
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship('Application', back_populates='specialty')
    entrance_exams = relationship('EntranceExam', back_populates='specialty')

class Applicant(Base):
    __tablename__ = 'applicants'
    __table_args__ = {'schema': 'university'}

    applicant_id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    birth_date = Column(Date, nullable=False)
    passport_number = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship('Application', back_populates='applicant')
    education_documents = relationship('EducationDocument', back_populates='applicant', cascade='all, delete-orphan')

class EducationDocument(Base):
    __tablename__ = 'education_documents'
    __table_args__ = {'schema': 'university'}

    document_id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey('university.applicants.applicant_id', ondelete='CASCADE'))
    document_type = Column(String(50), nullable=False)  # аттестат, диплом и т.д.
    document_number = Column(String(50), nullable=False)
    issue_date = Column(Date, nullable=False)
    issuing_organization = Column(String(200), nullable=False, default='')
    scan_path = Column(String(500))  # путь к файлу скана
    created_at = Column(DateTime, default=datetime.utcnow)

    applicant = relationship('Applicant', back_populates='education_documents')

class Application(Base):
    __tablename__ = 'applications'
    __table_args__ = {'schema': 'university'}

    application_id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer, ForeignKey('university.applicants.applicant_id', ondelete='CASCADE'))
    specialty_id = Column(Integer, ForeignKey('university.specialties.specialty_id', ondelete='RESTRICT'))
    status = Column(String(20), nullable=False, default='pending')
    submission_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applicant = relationship('Applicant', back_populates='applications')
    specialty = relationship('Specialty', back_populates='applications')
    exam_results = relationship('ExamResult', back_populates='application')

class ExamResult(Base):
    __tablename__ = 'exam_results'
    __table_args__ = {'schema': 'university'}

    result_id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('university.applications.application_id', ondelete='SET NULL'))
    exam_type = Column(String(50), nullable=False)  # ЕГЭ или вступительный
    subject = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    exam_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship('Application', back_populates='exam_results')

class EntranceExam(Base):
    __tablename__ = 'entrance_exams'
    __table_args__ = {'schema': 'university'}

    exam_id = Column(Integer, primary_key=True)
    specialty_id = Column(Integer, ForeignKey('university.specialties.specialty_id', ondelete='CASCADE'))
    subject = Column(String(100), nullable=False)
    min_score = Column(Integer, nullable=False)  # минимальный балл для сдачи
    created_at = Column(DateTime, default=datetime.utcnow)

    specialty = relationship('Specialty', back_populates='entrance_exams')

# События для валидации данных
@event.listens_for(Application, 'before_update')
def validate_application_status(mapper, connection, target):
    if target.status not in ['pending', 'under_review', 'approved', 'rejected']:
        raise ValueError('Invalid application status') 