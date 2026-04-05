from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import jwt
import bcrypt
from datetime import datetime, timedelta

from database import get_db, create_tables
from models import Usuario, Professor, Materia, Curso, Sala, Turma, Aula

create_tables()

SECRET = 'SECRET_KEY'
ALGO = 'HS256'

app = FastAPI(
    title='Horarios',
    description='API para gerenciamento de horários escolares',
    version='2.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

security = HTTPBearer()


class Login(BaseModel):
    email: str
    password: str

class AddUser(BaseModel):
    email: str
    password: str
    tipo: str
    professor_id: Optional[int] = None

class UpdateUser(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    tipo: Optional[str] = None
    professor_id: Optional[int] = None

class Nome(BaseModel):
    nome: str

class TurmaCreate(BaseModel):
    serie: Optional[int] = None
    curso_id: int
    letra: Optional[str] = None
    sala_id: int

class Sala(BaseModel):
    nome: str
    tipo: str

class AulaCreate(BaseModel):
    turma_id: int
    materia_id: int
    professores: List[int]
    dia_semana: int
    hora_inicio: str
    hora_fim: str
    subturma: Optional[str] = None
    sala_id: int

class AulaUpdate(BaseModel):
    turma_id: Optional[int] = None
    materia_id: Optional[int] = None
    professores: Optional[List[int]] = None
    dia_semana: Optional[int] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    subturma: Optional[str] = None
    sala_id: Optional[int] = None


def create_token(data):
    payload = data.copy()
    payload['exp'] = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def verify_token(credentials: HTTPAuthorizationCredentials=Depends(security)):
    try:
        return jwt.decode(credentials.credentials, SECRET, algorithms=[ALGO])
    except:
        raise HTTPException(401, 'Token invalido')

def admin_required(user=Depends(verify_token)):
    if user.get('tipo') != 'admin':
        raise HTTPException(403, 'Acesso negado')
    return user


@app.post('/login')
def login(data: Login, db: Session=Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not user or not bcrypt.checkpw(data.password.encode(), user.password_hash.encode()):
        raise HTTPException(401, 'Credenciais invalidas')

    token = create_token({'user_id': user.id, 'tipo': user.tipo})
    return {'token': token}

@app.get('/users')
def listar_users(db: Session=Depends(get_db), user=Depends(admin_required)):
    users = db.query(Usuario).all()
    return [
        {
            'id': u.id,
            'email': u.email,
            'tipo': u.tipo
        } for u in users
    ]

@app.post('/users')
def add_user(data: AddUser, db: Session=Depends(get_db), user=Depends(admin_required)):
    if data.tipo not in ['admin', 'professor']:
        raise HTTPException(400, 'Tipo invalido')

    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(400, 'Email ja existe')

    password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    new_user = Usuario(
        email=data.email,
        password_hash=password_hash,
        tipo=data.tipo
    )
    db.add(new_user)
    db.flush()

    if data.tipo == 'professor':
        if not data.professor_id:
            raise HTTPException(400, 'professor_id obrigatorio')

        prof = db.query(Professor).filter(Professor.id == data.professor_id).first()
        if not prof or prof.usuario_id:
            raise HTTPException(400, 'Professor invalido')

        prof.usuario_id = new_user.id

    db.commit()
    return {'id': new_user.id}

@app.put('/users/{id}')
def update_user(id: int, data: UpdateUser, db: Session=Depends(get_db), user=Depends(admin_required)):
    user_to_update = db.query(Usuario).filter(Usuario.id == id).first()
    if not user_to_update:
        raise HTTPException(404, 'Usuario nao encontrado')

    if data.email:
        if db.query(Usuario).filter(Usuario.email == data.email, Usuario.id != id).first():
            raise HTTPException(400, 'Email ja existe')
        user_to_update.email = data.email

    if data.password:
        user_to_update.password_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    if data.tipo:
        if data.tipo not in ['admin', 'professor']:
            raise HTTPException(400, 'Tipo invalido')
        user_to_update.tipo = data.tipo

    if data.professor_id is not None:
        prof = db.query(Professor).filter(Professor.id == data.professor_id).first()
        if not prof or (prof.usuario_id and prof.usuario_id != id):
            raise HTTPException(400, 'Professor invalido')
        
        if user_to_update.tipo == 'professor' and user_to_update.professor:
            user_to_update.professor.usuario_id = None
        
        if data.tipo == 'professor':
            prof.usuario_id = id
        else:
            prof.usuario_id = None

    db.commit()
    return {'ok': True}

@app.delete('/users/{id}')
def delete_user(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    user_to_delete = db.query(Usuario).filter(Usuario.id == id).first()
    if not user_to_delete:
        raise HTTPException(404, 'Usuario nao encontrado')

    if user_to_delete.tipo == 'professor' and user_to_delete.professor:
        user_to_delete.professor.usuario_id = None

    db.delete(user_to_delete)
    db.commit()
    return {'ok': True}


@app.get('/professores')
def listar_professores(db: Session=Depends(get_db)):
    professores = db.query(Professor).all()
    return [
        {
            'id': p.id,
            'nome': p.nome,
            'usuario_id': p.usuario_id
        } for p in professores
    ]

@app.post('/professores')
def criar_professor(data: Nome, db: Session=Depends(get_db), user=Depends(admin_required)):
    new_prof = Professor(nome=data.nome)
    db.add(new_prof)
    db.commit()
    return {'ok': True}

@app.put('/professores/{id}')
def atualizar_professor(id: int, data: Nome, db: Session=Depends(get_db), user=Depends(admin_required)):
    prof = db.query(Professor).filter(Professor.id == id).first()
    if not prof:
        raise HTTPException(404, 'Professor nao encontrado')
    
    prof.nome = data.nome
    db.commit()
    return {'ok': True}

@app.delete('/professores/{id}')
def deletar_professor(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    prof = db.query(Professor).filter(Professor.id == id).first()
    if not prof:
        raise HTTPException(404, 'Professor nao encontrado')
    
    db.delete(prof)
    db.commit()
    return {'ok': True}


@app.get('/materias')
def listar_materias(db: Session=Depends(get_db)):
    materias = db.query(Materia).all()
    return [{'id': m.id, 'nome': m.nome} for m in materias]

@app.post('/materias')
def criar_materia(data: Nome, db: Session=Depends(get_db), user=Depends(admin_required)):
    new_mat = Materia(nome=data.nome)
    db.add(new_mat)
    db.commit()
    return {'ok': True}

@app.put('/materias/{id}')
def atualizar_materia(id: int, data: Nome, db: Session=Depends(get_db), user=Depends(admin_required)):
    mat = db.query(Materia).filter(Materia.id == id).first()
    if not mat:
        raise HTTPException(404, 'Materia nao encontrada')
    
    mat.nome = data.nome
    db.commit()
    return {'ok': True}

@app.delete('/materias/{id}')
def deletar_materia(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    mat = db.query(Materia).filter(Materia.id == id).first()
    if not mat:
        raise HTTPException(404, 'Materia nao encontrada')
    
    db.delete(mat)
    db.commit()
    return {'ok': True}


@app.get('/cursos')
def listar_cursos(db: Session=Depends(get_db)):
    cursos = db.query(Curso).all()
    return [{'id': c.id, 'nome': c.nome} for c in cursos]

@app.post('/cursos')
def criar_curso(data: Nome, db: Session=Depends(get_db), user=Depends(admin_required)):
    new_curso = Curso(nome=data.nome)
    db.add(new_curso)
    db.commit()
    return {'ok': True}

@app.put('/cursos/{id}')
def atualizar_curso(id: int, data: Nome, db: Session=Depends(get_db), user=Depends(admin_required)):
    curso = db.query(Curso).filter(Curso.id == id).first()
    if not curso:
        raise HTTPException(404, 'Curso nao encontrado')
    
    curso.nome = data.nome
    db.commit()
    return {'ok': True}

@app.delete('/cursos/{id}')
def deletar_curso(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    curso = db.query(Curso).filter(Curso.id == id).first()
    if not curso:
        raise HTTPException(404, 'Curso nao encontrado')
    
    db.delete(curso)
    db.commit()
    return {'ok': True}


@app.get('/salas')
def listar_salas(db: Session=Depends(get_db)):
    salas = db.query(Sala).all()
    return [{'id': s.id, 'nome': s.nome, 'tipo': s.tipo} for s in salas]

@app.post('/salas')
def criar_sala(data: Sala, db: Session=Depends(get_db), user=Depends(admin_required)):
    new_sala = Sala(nome=data.nome, tipo=data.tipo)
    db.add(new_sala)
    db.commit()
    return {'ok': True}

@app.put('/salas/{id}')
def atualizar_sala(id: int, data: Sala, db: Session=Depends(get_db), user=Depends(admin_required)):
    sala = db.query(Sala).filter(Sala.id == id).first()
    if not sala:
        raise HTTPException(404, 'Sala nao encontrada')
    
    sala.nome = data.nome
    sala.tipo = data.tipo
    db.commit()
    return {'ok': True}

@app.delete('/salas/{id}')
def deletar_sala(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    sala = db.query(Sala).filter(Sala.id == id).first()
    if not sala:
        raise HTTPException(404, 'Sala nao encontrada')
    
    db.delete(sala)
    db.commit()
    return {'ok': True}


@app.get('/turmas')
def listar_turmas(db: Session=Depends(get_db)):
    turmas = db.query(Turma).all()
    return [
        {
            'id': t.id,
            'serie': t.serie,
            'curso_id': t.curso_id,
            'letra': t.letra,
            'sala_id': t.sala_id
        } for t in turmas
    ]

@app.post('/turmas')
def criar_turma(data: TurmaCreate, db: Session = Depends(get_db), user=Depends(admin_required)):
    new_turma = Turma(
        serie=data.serie,
        curso_id=data.curso_id,
        letra=data.letra,
        sala_id=data.sala_id
    )
    db.add(new_turma)
    db.commit()
    return {'id': new_turma.id}

@app.put('/turmas/{id}')
def atualizar_turma(id: int, data: TurmaCreate, db: Session = Depends(get_db), user=Depends(admin_required)):
    turma = db.query(Turma).filter(Turma.id == id).first()
    if not turma:
        raise HTTPException(404, 'Turma nao encontrada')
    
    turma.serie = data.serie
    turma.curso_id = data.curso_id
    turma.letra = data.letra
    turma.sala_id = data.sala_id
    db.commit()
    return {'ok': True}

@app.delete('/turmas/{id}')
def deletar_turma(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    turma = db.query(Turma).filter(Turma.id == id).first()
    if not turma:
        raise HTTPException(404, 'Turma nao encontrada')
    
    db.delete(turma)
    db.commit()
    return {'ok': True}


def verificar_conflito_horario(
        db: Session,
        turma_id: int,
        professores: List[int],
        dia: int,
        hora_inicio: str,
        hora_fim: str,
        sala_id: int,
        subturma: str = None
):    
    if subturma is None:
        conflito_turma = db.query(Aula).filter(
            Aula.turma_id == turma_id,
            Aula.dia_semana == dia,
            Aula.hora_inicio < hora_fim,
            Aula.hora_fim > hora_inicio
        ).first()
    else:
        conflito_turma = db.query(Aula).filter(
            Aula.turma_id == turma_id,
            Aula.subturma.is_(None),
            Aula.dia_semana == dia,
            Aula.hora_inicio < hora_fim,
            Aula.hora_fim > hora_inicio
        ).first()
    
    if conflito_turma:
        return 'Conflito turma'

    for prof_id in professores:
        conflito_prof = db.query(Aula).join(Aula.professores).filter(
            Professor.id == prof_id,
            Aula.dia_semana == dia,
            Aula.hora_inicio < hora_fim,
            Aula.hora_fim > hora_inicio
        ).first()
        
        if conflito_prof:
            return 'Conflito professor'

    conflito_sala = db.query(Aula).filter(
        Aula.sala_id == sala_id,
        Aula.dia_semana == dia,
        Aula.hora_inicio < hora_fim,
        Aula.hora_fim > hora_inicio
    ).first()
    
    if conflito_sala:
        return 'Conflito sala'

    return None


@app.get('/aulas')
def listar_aulas(
    dia: Optional[int] = None,
    hora_inicio: Optional[str] = None,
    hora_fim: Optional[str] = None,
    subturma: Optional[str] = None,
    sala_id: Optional[int] = None,
    db: Session=Depends(get_db)
):
    query = db.query(Aula)
    
    if dia:
        query = query.filter(Aula.dia_semana == dia)
    
    if hora_inicio:
        query = query.filter(Aula.hora_inicio >= hora_inicio)
    
    if hora_fim:
        query = query.filter(Aula.hora_fim <= hora_fim)
    
    if subturma:
        query = query.filter((Aula.subturma == subturma) | (Aula.subturma == None))
    
    if sala_id:
        query = query.filter(Aula.sala_id == sala_id)

    aulas = query.order_by(Aula.dia_semana, Aula.hora_inicio).all()
    
    return [
        {
            'id': a.id,
            'turma_id': a.turma_id,
            'materia_id': a.materia_id,
            'dia_semana': a.dia_semana,
            'hora_inicio': str(a.hora_inicio),
            'hora_fim': str(a.hora_fim),
            'subturma': a.subturma,
            'sala_id': a.sala_id,
            'professores': [p.id for p in a.professores]
        } for a in aulas
    ]

@app.post('/aulas')
def criar_aula(data: AulaCreate, db: Session=Depends(get_db), user=Depends(admin_required)):
    err = verificar_conflito_horario(db, data.turma_id, data.professores, data.dia_semana, data.hora_inicio, data.hora_fim, data.sala_id, data.subturma)
    if err:
        raise HTTPException(400, err)

    new_aula = Aula(
        turma_id=data.turma_id,
        materia_id=data.materia_id,
        dia_semana=data.dia_semana,
        hora_inicio=data.hora_inicio,
        hora_fim=data.hora_fim,
        subturma=data.subturma,
        sala_id=data.sala_id
    )
    db.add(new_aula)
    db.flush()

    professores = db.query(Professor).filter(Professor.id.in_(data.professores)).all()
    new_aula.professores.extend(professores)

    db.commit()
    return {'id': new_aula.id}

@app.put('/aulas/{id}')
def atualizar_aula(id: int, data: AulaUpdate, db: Session=Depends(get_db), user=Depends(admin_required)):
    aula = db.query(Aula).filter(Aula.id == id).first()
    if not aula:
        raise HTTPException(404, 'Aula nao encontrada')

    turma_id = data.turma_id if data.turma_id is not None else aula.turma_id
    materia_id = data.materia_id if data.materia_id is not None else aula.materia_id
    professores = data.professores if data.professores is not None else [p.id for p in aula.professores]
    dia_semana = data.dia_semana if data.dia_semana is not None else aula.dia_semana
    hora_inicio = data.hora_inicio if data.hora_inicio is not None else str(aula.hora_inicio)
    hora_fim = data.hora_fim if data.hora_fim is not None else str(aula.hora_fim)
    subturma = data.subturma if data.subturma is not None else aula.subturma
    sala_id = data.sala_id if data.sala_id is not None else aula.sala_id

    err = verificar_conflito_horario(db, turma_id, professores, dia_semana, hora_inicio, hora_fim, sala_id, subturma)
    if err:
        raise HTTPException(400, err)

    aula.turma_id = turma_id
    aula.materia_id = materia_id
    aula.dia_semana = dia_semana
    aula.hora_inicio = hora_inicio
    aula.hora_fim = hora_fim
    aula.subturma = subturma
    aula.sala_id = sala_id

    if data.professores is not None:
        nova_lista_professores = db.query(Professor).filter(Professor.id.in_(data.professores)).all()
        aula.professores.clear()
        aula.professores.extend(nova_lista_professores)

    db.commit()
    return {'ok': True}

@app.delete('/aulas/{id}')
def deletar_aula(id: int, db: Session=Depends(get_db), user=Depends(admin_required)):
    aula = db.query(Aula).filter(Aula.id == id).first()
    if not aula:
        raise HTTPException(404, 'Aula nao encontrada')
    
    db.delete(aula)
    db.commit()
    return {'ok': True}


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0')