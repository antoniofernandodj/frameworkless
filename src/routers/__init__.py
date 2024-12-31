from .consulta import ConsultaRouter
from .doenca import DoencaRouter
from .exame import ExameRouter
from .medicamento import MedicamentoRouter
from .paciente import PacienteRouter
from .tarefa import TarefaRouter
from .teste import TesteRouter



__all__ = [
    'ConsultaRouter',
    'DoencaRouter',
    'ExameRouter',
    'MedicamentoRouter',
    'PacienteRouter',
    'TarefaRouter',
    'TesteRouter'
]
