import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from csv import DictReader, DictWriter

from models import *

DATA_DIR = 'dados/'

DATABASE_URL = 'mysql+pymysql://root:@localhost/horarios'
engine = create_engine(DATABASE_URL, echo=False)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


def ler_ordenar(path, lambda_key):
    arquivo = f'{DATA_DIR}{path}.csv'

    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = DictReader(f)
        fieldnames = reader.fieldnames
        dados = sorted(reader, key=lambda_key)

    with open(arquivo, 'w', encoding='utf-8', newline='') as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dados)

    return dados


usuarios = ler_ordenar('usuarios', lambda x: (x['tipo'], x['email']))
for x in usuarios:
    x['password_hash'] = bcrypt.hashpw(x['password_hash'].encode(), bcrypt.gensalt()).decode()

professores = ler_ordenar('professores', lambda x: x['nome'])
materias = ler_ordenar('materias', lambda x: x['nome'])
cursos = ler_ordenar('cursos', lambda x: x['nome'])
salas = ler_ordenar('salas', lambda x: x['nome'])
turmas = ler_ordenar('turmas', lambda x: (x['serie'], x['curso_id'], x['letra'] or ''))
aulas = ler_ordenar('aulas', lambda x: (x['turma_id'], x['dia_semana'], x['hora_inicio'], x['subturma'] or ''))

professor_materia = ler_ordenar('professor_materia', lambda x: (x['professor_id'], x['materia_id']))
aula_professor = ler_ordenar('aula_professor', lambda x: x['aula_id'])

restricoes_curso = ler_ordenar('restricoes_curso', lambda x: (x['curso_id'], x['dia_semana'], x['hora_inicio']))
restricoes_professor = ler_ordenar('restricoes_professor', lambda x: (x['professor_id'], x['dia_semana'], x['hora_inicio']))


for u in usuarios:
    novo_user = Usuario(
        email=u['email'],
        password_hash=u['password_hash'],
        tipo=u['tipo']
    )
    db.add(novo_user)
db.commit()

for p in professores:
    novo_prof = Professor(nome=p['nome'])
    db.add(novo_prof)
db.commit()

for m in materias:
    nova_mat = Materia(nome=m['nome'])
    db.add(nova_mat)
db.commit()

for pm in professor_materia:
    db.execute(
        professor_materia_table.insert().values(
            professor_id=int(pm['professor_id']),
            materia_id=int(pm['materia_id'])
        )
    )
db.commit()

for c in cursos:
    novo_curso = Curso(nome=c['nome'])
    db.add(novo_curso)
db.commit()

for s in salas:
    nova_sala = Sala(nome=s['nome'], tipo=s['tipo'])
    db.add(nova_sala)
db.commit()

for t in turmas:
    nova_turma = Turma(
        serie=int(t['serie']) if t['serie'] else None,
        curso_id=int(t['curso_id']),
        letra=t['letra'] if t['letra'] else None,
        sala_id=int(t['sala_id']) if t['sala_id'] else None
    )
    db.add(nova_turma)
db.commit()

for a in aulas:
    nova_aula = Aula(
        turma_id=int(a['turma_id']),
        materia_id=int(a['materia_id']),
        dia_semana=int(a['dia_semana']),
        hora_inicio=a['hora_inicio'],
        hora_fim=a['hora_fim'],
        subturma=a['subturma'] if a['subturma'] else None,
        sala_id=int(a['sala_id'])
    )
    db.add(nova_aula)
db.commit()

for ap in aula_professor:
    db.execute(
        aula_professor_table.insert().values(
            aula_id=int(ap['aula_id']),
            professor_id=int(ap['professor_id'])
        )
    )
db.commit()

for rc in restricoes_curso:
    nova_r = RestricaoCurso(
        curso_id=int(rc['curso_id']),
        dia_semana=int(rc['dia_semana']),
        hora_inicio=rc['hora_inicio'],
        hora_fim=rc['hora_fim']
    )
    db.add(nova_r)
db.commit()

for rp in restricoes_professor:
    nova_r = RestricaoProfessor(
        professor_id=int(rp['professor_id']),
        dia_semana=int(rp['dia_semana']),
        hora_inicio=rp['hora_inicio'],
        hora_fim=rp['hora_fim']
    )
    db.add(nova_r)
db.commit()

db.close()