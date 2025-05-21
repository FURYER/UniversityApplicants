-- Создание схемы
CREATE SCHEMA IF NOT EXISTS university;

-- Создание таблицы специальностей
CREATE TABLE university.specialties (
    specialty_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    faculty VARCHAR(100) NOT NULL,
    seats_available INTEGER NOT NULL CHECK (seats_available >= 0),
    study_form VARCHAR(20) NOT NULL DEFAULT 'full_time' CHECK (study_form IN ('full_time', 'part_time', 'distance')),
    tuition_fee INTEGER,
    passing_score INTEGER CHECK (passing_score >= 0 AND passing_score <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы вступительных экзаменов
CREATE TABLE university.entrance_exams (
    exam_id SERIAL PRIMARY KEY,
    specialty_id INTEGER REFERENCES university.specialties(specialty_id) ON DELETE CASCADE,
    subject VARCHAR(50) NOT NULL,
    min_score INTEGER NOT NULL CHECK (min_score >= 0 AND min_score <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы абитуриентов
CREATE TABLE university.applicants (
    applicant_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    birth_date DATE NOT NULL,
    passport_number VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы документов об образовании
CREATE TABLE university.education_documents (
    document_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES university.applicants(applicant_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL,
    issuing_organization VARCHAR(200) NOT NULL DEFAULT '',
    scan_path VARCHAR(500),
    average_score DECIMAL(4,2) CHECK (average_score >= 0 AND average_score <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы заявлений
CREATE TABLE university.applications (
    application_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES university.applicants(applicant_id) ON DELETE CASCADE,
    specialty_id INTEGER REFERENCES university.specialties(specialty_id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'approved', 'rejected')),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы результатов экзаменов
CREATE TABLE university.exam_results (
    result_id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES university.applications(application_id) ON DELETE CASCADE,
    exam_type VARCHAR(50) NOT NULL DEFAULT 'ЕГЭ',
    subject VARCHAR(50) NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    exam_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX idx_applicants_passport ON university.applicants(passport_number);
CREATE INDEX idx_applications_status ON university.applications(status);
CREATE INDEX idx_exam_results_application ON university.exam_results(application_id);
CREATE INDEX idx_entrance_exams_specialty ON university.entrance_exams(specialty_id);

-- Создание триггерной функции для обновления updated_at
CREATE OR REPLACE FUNCTION university.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггера для обновления updated_at
CREATE TRIGGER update_applications_updated_at
    BEFORE UPDATE ON university.applications
    FOR EACH ROW
    EXECUTE FUNCTION university.update_updated_at_column();

-- Создание представления для просмотра статистики по специальностям
CREATE VIEW university.specialty_statistics AS
SELECT 
    s.specialty_id,
    s.name as specialty_name,
    s.faculty,
    s.seats_available,
    s.tuition_fee,
    s.passing_score,
    COUNT(a.application_id) as total_applications,
    COUNT(CASE WHEN a.status = 'approved' THEN 1 END) as approved_applications,
    COUNT(DISTINCT e.exam_id) as total_exams
FROM university.specialties s
LEFT JOIN university.applications a ON s.specialty_id = a.specialty_id
LEFT JOIN university.entrance_exams e ON s.specialty_id = e.specialty_id
GROUP BY s.specialty_id, s.name, s.faculty, s.seats_available, s.tuition_fee, s.passing_score;

-- Создание функции для проверки доступности мест
CREATE OR REPLACE FUNCTION university.check_available_seats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'approved' THEN
        IF (SELECT COUNT(*) FROM university.applications 
            WHERE specialty_id = NEW.specialty_id AND status = 'approved') > 
           (SELECT seats_available FROM university.specialties WHERE specialty_id = NEW.specialty_id) THEN
            RAISE EXCEPTION 'No available seats for this specialty';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггера для проверки доступности мест
CREATE TRIGGER check_seats_before_approval
    BEFORE UPDATE ON university.applications
    FOR EACH ROW
    EXECUTE FUNCTION university.check_available_seats(); 