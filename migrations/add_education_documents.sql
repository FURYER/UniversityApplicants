-- Создание таблицы документов об образовании
CREATE TABLE university.education_documents (
    document_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES university.applicants(applicant_id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL,
    issuing_organization VARCHAR(200) NOT NULL,
    scan_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы результатов экзаменов
CREATE TABLE university.exam_results (
    result_id SERIAL PRIMARY KEY,
    applicant_id INTEGER REFERENCES university.applicants(applicant_id) ON DELETE CASCADE,
    exam_type VARCHAR(50) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    exam_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации поиска
CREATE INDEX idx_education_documents_applicant ON university.education_documents(applicant_id);
CREATE INDEX idx_exam_results_applicant ON university.exam_results(applicant_id);

-- Создание директории для хранения сканов документов
-- Примечание: эту директорию нужно создать вручную
-- mkdir -p uploads/education_documents 