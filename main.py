from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mysql.connector import pooling, Error
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host='localhost',
    user='root',
    password='',
    database='horarios'
)

def get_db():
    try:
        return pool.get_connection()
    except Error:
        raise HTTPException(500, 'Erro no banco')


def fmt(h):
    return str(h)[:-3] if h else None


def parse_turma(t: str):
    partes = t.split('_')

    serie = None
    curso = None
    letra = None
    subturma = None

    for p in partes:
        if p.isdigit():
            serie = int(p)
        elif p in ['A', 'B', 'C']:
            if not letra:
                letra = p
            else:
                subturma = p
        else:
            curso = p

    if not curso:
        raise HTTPException(400, 'Curso é obrigatório')

    return serie, curso, letra, subturma


BASE = '''
SELECT
    a.id,
    a.dia_semana,
    a.hora_inicio,
    a.hora_fim,
    m.nome materia,
    GROUP_CONCAT(p.nome) professores,
    t.serie,
    c.nome curso,
    t.letra,
    a.subturma,

    COALESCE(sa.nome, st.nome) AS sala,
    COALESCE(sa.tipo, st.tipo) AS tipo_sala

FROM aulas a
JOIN turmas t ON a.turma_id = t.id
JOIN cursos c ON t.curso_id = c.id
JOIN materias m ON a.materia_id = m.id

LEFT JOIN salas sa ON a.sala_id = sa.id
LEFT JOIN salas st ON t.sala_id = st.id

LEFT JOIN aula_professor ap ON a.id = ap.aula_id
LEFT JOIN professores p ON ap.professor_id = p.id
'''


@app.get('/')
def root():
    return {
        'status': 'ok',
        'api': 'Horários',
        'endpoints': [
            '/professores',
            '/materias',
            '/cursos',
            '/turmas',
            '/salas',
            '/aulas',
            '/entrada-saida'
        ]
    }


@app.get('/professores')
def professores(nome: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if nome:
            cursor.execute(
                '''SELECT nome FROM professores 
                   WHERE MATCH(nome) AGAINST (%s IN BOOLEAN MODE)
                   ORDER BY nome''',
                (f'+{nome}*',)
            )
        else:
            cursor.execute('SELECT nome FROM professores ORDER BY nome')

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get('/materias')
def materias(nome: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if nome:
            cursor.execute(
                '''SELECT nome FROM materias 
                   WHERE MATCH(nome) AGAINST (%s IN BOOLEAN MODE)
                   ORDER BY nome''',
                (f'+{nome}*',)
            )
        else:
            cursor.execute('SELECT nome FROM materias ORDER BY nome')

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get('/cursos')
def cursos(nome: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if nome:
            cursor.execute(
                '''SELECT nome FROM cursos 
                   WHERE MATCH(nome) AGAINST (%s IN BOOLEAN MODE)
                   ORDER BY nome''',
                (f'+{nome}*',)
            )
        else:
            cursor.execute('SELECT nome FROM cursos ORDER BY nome')

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get('/turmas')
def turmas(turma: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        where = []
        params = []

        if turma:
            serie, curso, letra, _ = parse_turma(turma)

            where.append('MATCH(c.nome) AGAINST (%s IN BOOLEAN MODE)')
            params.append(f'+{curso}*')

            if serie:
                where.append('t.serie=%s')
                params.append(serie)

            if letra:
                where.append('t.letra=%s')
                params.append(letra)

        where_sql = f'WHERE {" AND ".join(where)}' if where else ''

        cursor.execute(f'''
        SELECT t.serie, c.nome curso, t.letra
        FROM turmas t
        JOIN cursos c ON t.curso_id = c.id
        {where_sql}
        ORDER BY c.nome, t.serie, t.letra
        ''', tuple(params))

        result = cursor.fetchall()

        for i, t in enumerate(result):
            result[i]['nome'] = '_'.join([str(v) for v in t.values() if v])

        return result
    finally:
        cursor.close()
        conn.close()


@app.get('/salas')
def salas(nome: Optional[str] = None, tipo: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        where = []
        params = []

        if nome:
            where.append('MATCH(nome) AGAINST (%s IN BOOLEAN MODE)')
            params.append(f'+{nome}*')

        if tipo:
            where.append('tipo = %s')
            params.append(tipo)

        where_sql = f'WHERE {" AND ".join(where)}' if where else ''

        cursor.execute(f'''
            SELECT nome, tipo
            FROM salas
            {where_sql}
            ORDER BY nome
        ''', tuple(params))

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get('/aulas')
def aulas(
    turma: Optional[str] = None,
    professor: Optional[str] = None,
    dia: Optional[int] = Query(None, ge=1, le=5),
    materia: Optional[str] = None,
    hora_inicio: Optional[str] = None,
    hora_fim: Optional[str] = None,
    sala: Optional[str] = None,
    tipo_sala: Optional[str] = None,
):
    where = []
    params = []

    if turma:
        serie, curso, letra, subturma = parse_turma(turma)

        where.append('MATCH(c.nome) AGAINST (%s IN BOOLEAN MODE)')
        params.append(f'+{curso}*')

        if serie:
            where.append('t.serie=%s')
            params.append(serie)

        if letra:
            where.append('t.letra=%s')
            params.append(letra)

        if subturma:
            where.append('(a.subturma IS NULL OR a.subturma=%s)')
            params.append(subturma)

    if professor:
        where.append('MATCH(p.nome) AGAINST (%s IN BOOLEAN MODE)')
        params.append(f'+{professor}*')

    if dia:
        where.append('a.dia_semana=%s')
        params.append(dia)

    if materia:
        where.append('MATCH(m.nome) AGAINST (%s IN BOOLEAN MODE)')
        params.append(f'+{materia}*')

    if hora_inicio:
        where.append('a.hora_inicio=%s')
        params.append(hora_inicio)

    if hora_fim:
        where.append('a.hora_fim=%s')
        params.append(hora_fim)

    if sala:
        where.append('MATCH(COALESCE(sa.nome, st.nome)) AGAINST (%s IN BOOLEAN MODE)')
        params.append(f'+{sala}*')

    if tipo_sala:
        where.append('COALESCE(sa.tipo, st.tipo) = %s')
        params.append(tipo_sala)

    where_sql = f'WHERE {" AND ".join(where)}' if where else ''

    query = f'''
    {BASE}
    {where_sql}
    GROUP BY a.id
    ORDER BY a.dia_semana, a.hora_inicio
    '''

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(params))
        response = cursor.fetchall()

        for r in response:
            r['hora_inicio'] = fmt(r['hora_inicio'])
            r['hora_fim'] = fmt(r['hora_fim'])

        return response
    finally:
        cursor.close()
        conn.close()


@app.get('/entrada-saida')
def entrada_saida(
    turma: Optional[str] = None,
    professor: Optional[str] = None,
    dia: Optional[int] = Query(None, ge=1, le=5)
):
    if not turma and not professor:
        raise HTTPException(400, 'Informe turma ou professor')

    where = []
    params = []

    if turma:
        serie, curso, letra, subturma = parse_turma(turma)

        where.append('MATCH(c.nome) AGAINST (%s IN BOOLEAN MODE)')
        params.append(f'+{curso}*')

        if serie:
            where.append('t.serie=%s')
            params.append(serie)

        if letra:
            where.append('t.letra=%s')
            params.append(letra)

        if subturma:
            where.append('(a.subturma IS NULL OR a.subturma=%s)')
            params.append(subturma)

    if professor:
        where.append('MATCH(p.nome) AGAINST (%s IN BOOLEAN MODE)')
        params.append(f'+{professor}*')

    if dia:
        where.append('a.dia_semana=%s')
        params.append(dia)

    query = f'''
    SELECT
        a.dia_semana,
        MIN(a.hora_inicio) entrada,
        MAX(a.hora_fim) saida
    FROM aulas a
    JOIN turmas t ON a.turma_id = t.id
    JOIN cursos c ON t.curso_id = c.id
    LEFT JOIN aula_professor ap ON a.id = ap.aula_id
    LEFT JOIN professores p ON ap.professor_id = p.id
    WHERE {' AND '.join(where)}
    GROUP BY a.dia_semana
    ORDER BY a.dia_semana
    '''

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, tuple(params))
        response = cursor.fetchall()

        for r in response:
            r['entrada'] = fmt(r['entrada'])
            r['saida'] = fmt(r['saida'])

        return response
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    from uvicorn import run
    run('main:app', host='0.0.0.0', reload=True)