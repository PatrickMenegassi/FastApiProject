from datetime import datetime
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.categoria.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.models import AtletaModel
from fastapi_pagination import LimitOffsetPage, paginate

router = APIRouter()

# Adicionar novo atleta
@router.post(
        path='/', 
        summary='Criar um novo atleta', 
        status_code=status.HTTP_201_CREATED,
        response_model=AtletaOut)

async def post(db_session: DatabaseDependency, atleta_in: AtletaIn):
    categoria_name = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome
    cpf_novo = atleta_in.cpf

    categoria = (await db_session.execute(select(CategoriaModel).filter_by(nome=categoria_name))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'A categoria {categoria_name} não foi encontrada.')
    
    centro_treinamento = (await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'A centro de treinamento {centro_treinamento_nome} não foi encontrado.')
    
    cpf_existente =  (await db_session.execute(select(AtletaModel).filter_by(cpf=cpf_novo))).scalars().first()

    if cpf_existente:
        raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail=f"Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}"
            )
    
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(),**atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        
        db_session.add(atleta_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Ocorreu um erro ao inserir os dados no banco')

    return atleta_out

# Procurar todos
@router.get(
        path='/', 
        summary='Consultar todos os atletas', 
        status_code=status.HTTP_200_OK, 
        response_model=list[AtletaOut],
)

async def query(
    db_session: DatabaseDependency, 
    nome: Optional[str] = None,
    cpf: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
    ) -> LimitOffsetPage[list[AtletaOut]]:
    query = select(AtletaModel).options(
        joinedload(AtletaModel.centro_treinamento),
        joinedload(AtletaModel.categoria)
    )
    
    if nome:
        query = query.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    
    if cpf:
        query = query.filter(AtletaModel.cpf == cpf)
    
    query = query.offset(offset).limit(limit)

    result = await db_session.execute(query)
    atletas = result.scalars().all()

    return [
        AtletaOut(
            nome=atleta.nome,
            centro_treinamento=atleta.centro_treinamento.nome, 
            categoria=atleta.categoria.nome                    
        ) for atleta in atletas
    ]


# Procurar por ID
@router.get(
        path='/{id}', 
        summary='Consultar atleta por Id', 
        status_code=status.HTTP_200_OK, 
        response_model=AtletaOut,
)

async def query(
    id: UUID4,
    db_session: DatabaseDependency, 
    ) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrada no id: {id}')

    return atleta

@router.patch(
        path='/{id}', 
        summary='Editar um atleta por Id', 
        status_code=status.HTTP_200_OK, 
        response_model=AtletaOut,
)

async def query(
    id: UUID4,
    db_session: DatabaseDependency,
    atleta_up: AtletaUpdate = Body(...)
    ) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrada no id: {id}')
    
    atleta_uptdate = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_uptdate.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
        path='/{id}', 
        summary='Deletar atleta por Id', 
        status_code=status.HTTP_204_NO_CONTENT
)

async def query(
    id: UUID4,
    db_session: DatabaseDependency, 
    ) -> None:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrada no id: {id}')
    
    await db_session.delete(atleta)
    await db_session.commit()