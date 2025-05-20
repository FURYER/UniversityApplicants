-- Добавление новых полей в таблицу specialties
ALTER TABLE university.specialties
ADD COLUMN study_form VARCHAR(50) NOT NULL DEFAULT 'очная',
ADD COLUMN tuition_fee INTEGER NOT NULL DEFAULT 0,
ADD COLUMN passing_score INTEGER;

-- Создание таблицы вступительных экзаменов
CREATE TABLE university.entrance_exams (
    exam_id SERIAL PRIMARY KEY,
    specialty_id INTEGER REFERENCES university.specialties(specialty_id) ON DELETE CASCADE,
    subject VARCHAR(100) NOT NULL,
    min_score INTEGER NOT NULL CHECK (min_score >= 0 AND min_score <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индекса для быстрого поиска экзаменов по специальности
CREATE INDEX idx_entrance_exams_specialty ON university.entrance_exams(specialty_id); 