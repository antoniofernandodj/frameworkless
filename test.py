from datetime import date
from src.repository import Paciente, PacienteRepository
from src.infra.database import SessionLocal


with SessionLocal() as session:
    repo = PacienteRepository(session)

    paciente0 = repo.create(Paciente(1, 'antonio', date(1,2,3), 'F'))

    print(paciente0)

    paciente1 = repo.get_by_id(1)

    assert paciente1

    paciente1.update_from_dict({'nome': 'Antonio Fernando'})

    paciente2 = repo.get_by_id(1)

    assert paciente2

    print(paciente2)

    repo.delete(paciente2.id)

    paciente3 = repo.get_by_id(1)

    assert paciente3 is None

    print(paciente3)