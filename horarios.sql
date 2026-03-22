DROP DATABASE IF EXISTS horarios;
CREATE DATABASE IF NOT EXISTS horarios
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE horarios;

CREATE TABLE professores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serie TINYINT UNSIGNED,
    curso ENUM('curso1', 'curso2') NOT NULL,
    letra ENUM('A', 'B', 'C'),

    CHECK (serie IS NULL OR serie BETWEEN 1 AND 10)
);

CREATE TABLE aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    turma_id INT,
    materia VARCHAR(100) NOT NULL,

    dia_semana TINYINT UNSIGNED NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    CHECK (dia_semana BETWEEN 0 AND 4),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE aula_professor (
    aula_id INT,
    professor_id INT,

    PRIMARY KEY (aula_id, professor_id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON UPDATE CASCADE ON DELETE CASCADE
);