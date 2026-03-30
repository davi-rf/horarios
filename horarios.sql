DROP DATABASE IF EXISTS horarios;
CREATE DATABASE horarios
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE horarios;

CREATE TABLE professores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    FULLTEXT (nome)
);

CREATE TABLE materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    FULLTEXT (nome)
);

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    FULLTEXT (nome)
);

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    tipo ENUM('sala', 'lab', 'quadra', 'outro') DEFAULT 'sala' NOT NULL,

    FULLTEXT (nome),
    INDEX idx_salas_tipo (tipo)
);

CREATE TABLE turmas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serie TINYINT UNSIGNED,
    curso_id INT NOT NULL,
    letra ENUM('A', 'B', 'C'),

    sala_id INT, -- sala padrão da turma

    CHECK (serie IS NULL OR serie BETWEEN 1 AND 10),

    UNIQUE (serie, curso_id, letra),

    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_turma_curso (curso_id),
    INDEX idx_turma_serie (serie),
    INDEX idx_turma_letra (letra),
    INDEX idx_turma_sala (sala_id)
);

CREATE TABLE aulas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    turma_id INT NOT NULL,
    materia_id INT,

    dia_semana TINYINT UNSIGNED NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,

    subturma ENUM('A', 'B'),
    sala_id INT, -- sobrescreve sala da turma (opcional)

    CHECK (dia_semana BETWEEN 1 AND 5),
    CHECK (hora_inicio < hora_fim),

    FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE SET NULL ON UPDATE CASCADE,

    INDEX idx_aulas_turma (turma_id),
    INDEX idx_aulas_materia (materia_id),
    INDEX idx_aulas_dia (dia_semana),
    INDEX idx_aulas_horario (hora_inicio, hora_fim),
    INDEX idx_aulas_sala (sala_id)
);

CREATE TABLE aula_professor (
    aula_id INT,
    professor_id INT,

    PRIMARY KEY (aula_id, professor_id),

    FOREIGN KEY (aula_id) REFERENCES aulas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE ON UPDATE CASCADE,

    INDEX idx_ap_aula (aula_id),
    INDEX idx_ap_professor (professor_id)
);