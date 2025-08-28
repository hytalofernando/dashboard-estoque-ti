"""
Modelos de dados para o Dashboard Estoque TI
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class StatusEquipamento(str, Enum):
    """Status do equipamento"""
    DISPONIVEL = "Disponível"
    INDISPONIVEL = "Indisponível"
    MANUTENCAO = "Manutenção"

class TipoMovimentacao(str, Enum):
    """Tipo de movimentação"""
    ENTRADA = "Entrada"
    SAIDA = "Saída"

class CondicionEquipamento(str, Enum):
    """Condição do equipamento - Novo ou Usado"""
    NOVO = "Novo"
    USADO = "Usado"

class Equipamento(BaseModel):
    """Modelo para equipamento com condição Novo/Usado"""
    id: Optional[int] = None
    equipamento: str = Field(..., min_length=1, max_length=100)
    categoria: str = Field(..., min_length=1)
    marca: str = Field(..., min_length=1, max_length=50)
    modelo: str = Field(..., min_length=1, max_length=50)
    codigo_produto: str = Field(..., min_length=2, max_length=20)
    quantidade: int = Field(..., ge=1, le=1000)
    valor_unitario: float = Field(..., gt=0)
    data_chegada: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    fornecedor: str = Field(..., min_length=1, max_length=100)
    status: str = "Disponível"
    condicao: CondicionEquipamento = Field(default=CondicionEquipamento.NOVO, description="Condição do equipamento: Novo ou Usado")
    
    @field_validator('codigo_produto')
    @classmethod
    def codigo_produto_valido(cls, v):
        """Valida formato do código do produto"""
        if not v or len(v.strip()) < 2:
            raise ValueError('Código do produto deve ter pelo menos 2 caracteres')
        return v.strip().upper()
    
    @field_validator('quantidade')
    @classmethod
    def quantidade_valida(cls, v):
        """Valida quantidade"""
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        if v > 1000:
            raise ValueError('Quantidade máxima é 1000 unidades')
        return v

class Movimentacao(BaseModel):
    """Modelo para movimentação com rastreamento de condição"""
    id: Optional[int] = None
    equipamento_id: int = Field(..., gt=0)
    tipo_movimentacao: TipoMovimentacao
    quantidade: int = Field(..., gt=0)
    data_movimentacao: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    destino_origem: str = Field(..., min_length=1, max_length=100)
    observacoes: Optional[str] = Field(None, max_length=500)
    codigo_produto: Optional[str] = None
    condicao: CondicionEquipamento = Field(default=CondicionEquipamento.NOVO, description="Condição do equipamento movimentado: Novo ou Usado")
    
    @field_validator('observacoes')
    @classmethod
    def observacoes_validas(cls, v):
        """Valida observações"""
        if v and len(v) > 500:
            raise ValueError('Observações não podem exceder 500 caracteres')
        return v

class EquipamentoResponse(BaseModel):
    """Resposta de operação em equipamento"""
    success: bool
    message: str
    equipamento: Optional[dict] = None
    nova_quantidade: Optional[int] = None

class MovimentacaoResponse(BaseModel):
    """Resposta de operação de movimentação"""
    success: bool
    message: str
    movimentacao: Optional[Movimentacao] = None 