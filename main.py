from mysql.connector import connect

connection = connect(
    host='localhost',
    user='root',
    password='',
    database='horarios',
    charset='utf8mb4'
)
cursor = connection.cursor(dictionary=True)

BASE_QUERY = '''
    SELECT a.id, a.dia_semana, a.hora_inicio, a.hora_fim, a.materia,
           t.serie, t.curso, t.letra,
           GROUP_CONCAT(p.nome SEPARATOR ', ') as professores
    FROM aulas a
    JOIN turmas t ON a.turma_id = t.id
    LEFT JOIN aula_professor ap ON a.id = ap.aula_id
    LEFT JOIN professores p ON ap.professor_id = p.id
'''
TRACOS = '-' * 45


def print_aulas():
    print(f'\n{TRACOS} AULAS ENCONTRADAS {TRACOS}\n')
    
    aulas = cursor.fetchall()
    if not aulas:
        print('Nenhuma aula encontrada.')
        return

    dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
    for aula in aulas:
        dia_str = dias[int(aula['dia_semana'])]
        prof = aula['professores']
        serie_val = aula['serie']
        curso_val = aula['curso']
        letra_val = aula['letra']
        
        serie = f'{serie_val}º ' if serie_val else ''
        letra = f' {letra_val}' if letra_val else ''
        turma = f'{serie}{curso_val}{letra}'
        
        materia = aula['materia']
        inicio = aula['hora_inicio']
        fim = aula['hora_fim']

        print(f'[{dia_str}] {inicio} - {fim} | Turma: {turma} | Prof(s): {prof} | Matéria: {materia}')
    
    print('\n')


def buscar_aulas(base):
    if base == 1:
        filtro_valor = input('ID da Turma: ')
        filtro_sql = 't.id = %s'
    else:
        filtro_valor = '%' + input('Nome do Professor (ou parte dele): ') + '%'
        filtro_sql = 'p.nome LIKE %s'

    dia = input('Dia da semana [0=Segunda ... 4=Sexta] (Deixe em branco para todos os dias): ').strip()

    query = BASE_QUERY + ' WHERE ' + filtro_sql
    params = [filtro_valor]

    if dia:
        query += ' AND a.dia_semana = %s'
        params.append(dia)

    query += ' GROUP BY a.id ORDER BY a.dia_semana, a.hora_inicio'
    
    cursor.execute(query, tuple(params))
    print_aulas()


def buscar_horarios(base):
    if base == 1:
        filtro_valor = input('ID da Turma: ')
        filtro_sql = 't.id = %s'
        
        query = '''
            SELECT a.dia_semana, t.serie, t.curso, t.letra, MIN(a.hora_inicio) entrada, MAX(a.hora_fim) saida
            FROM aulas a
            JOIN turmas t ON a.turma_id = t.id
            WHERE ''' + filtro_sql
    else:
        filtro_valor = '%' + input('Nome do Professor (ou parte dele): ') + '%'
        filtro_sql = 'p.nome LIKE %s'
        
        query = '''
            SELECT a.dia_semana, p.nome professor, MIN(a.hora_inicio) entrada, MAX(a.hora_fim) saida
            FROM aulas a
            JOIN aula_professor ap ON a.id = ap.aula_id
            JOIN professores p ON ap.professor_id = p.id
            WHERE ''' + filtro_sql

    dia = input('Dia da semana [0=Segunda ... 4=Sexta] (Deixe em branco para todos os dias): ').strip()
    
    params = [filtro_valor]
    if dia:
        query += ' AND a.dia_semana = %s'
        params.append(dia)
        
    if base == 1:
        query += ' GROUP BY a.dia_semana, t.id ORDER BY a.dia_semana'
    else:
        query += ' GROUP BY a.dia_semana, p.id ORDER BY a.dia_semana'
        
    cursor.execute(query, tuple(params))
    
    resultados = cursor.fetchall()
    print(f'\n{TRACOS} HORÁRIOS ENCONTRADOS {TRACOS}\n')
    
    if not resultados:
        print('Nenhum horário encontrado.')
        return
        
    dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
    for r in resultados:
        dia_str = dias[int(r['dia_semana'])]
        entrada = r['entrada']
        saida = r['saida']
        
        if base == 1:
            serie_val = r['serie']
            curso_val = r['curso']
            letra_val = r['letra']
            serie = f'{serie_val}º ' if serie_val else ''
            letra = f' {letra_val}' if letra_val else ''
            alvo = f'Turma: {serie}º {curso_val} {letra}'.strip() if serie != '' else f'Turma: {curso_val} {letra}'.strip()
        else:
            prof = r['professor']
            alvo = f'Prof(s): {prof}'
            
        print(f'[{dia_str}] Entrada: {entrada} | Saída: {saida} | {alvo}')
        
    print('\n')


while True:
    TRACOS = '-' * 45
    print(f'''{TRACOS} MENU {TRACOS}

Qual tipo de pesquisa deseja fazer?
  1 - Aulas
  2 - Horários de chegada e de saída
  0 - Sair

''')

    try:
        tipo = int(input('Sua escolha: ').strip()[0])
    except (ValueError, IndexError):
        print('Opção inválida.')
        continue

    if tipo == 0: break
    if tipo not in (1, 2):
        print('Opção inválida.')
        continue

    print('''
Com base em que?
  1 - Turma
  2 - Professor
  0 - Voltar
''')

    try:
        base = int(input('Sua escolha: ').strip()[0])
    except (ValueError, IndexError):
        print('Opção inválida.')
        continue

    if base == 0: continue
    if base not in (1, 2):
        print('Opção inválida.')
        continue

    if tipo == 1: buscar_aulas(base)
    elif tipo == 2: buscar_horarios(base)


cursor.close()
connection.close()