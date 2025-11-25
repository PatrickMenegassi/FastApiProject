from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from pydantic import UUID4
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        path='/', 
        summary='Criar um novo centro de treinamento', 
        status_code=status.HTTP_201_CREATED, 
        response_model=CentroTreinamentoOut,
)

async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
    ) -> CentroTreinamentoOut:

    categoria_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    categoria_model = CentroTreinamentoModel(**categoria_out.model_dump())

    db_session.add(categoria_model)
    await db_session.commit()

    return categoria_out

@router.get(
        path='/', 
        summary='Consultar todos os centros de treinamento', 
        status_code=status.HTTP_200_OK, 
        response_model=list[CentroTreinamentoOut],
)

async def query(
    db_session: DatabaseDependency, 
    ) -> list[CentroTreinamentoOut]:
    categorias: list[CentroTreinamentoOut] = (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    return categorias

@router.get(
        path='/{id}', 
        summary='Consultar categoria por Id', 
        status_code=status.HTTP_200_OK, 
        response_model=CentroTreinamentoOut,
)

async def query(
    id: UUID4,
    db_session: DatabaseDependency, 
    ) -> CentroTreinamentoOut:
    categoria: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Centro de treinamento não encontrado no id: {id}')

    return categoria