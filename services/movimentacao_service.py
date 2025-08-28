"""
Serviço para gerenciar movimentações de estoque
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from models.schemas import Movimentacao, MovimentacaoResponse

class MovimentacaoService:
    """Serviço para gerenciar movimentações"""
    
    def __init__(self, df_movimentacoes: Optional[pd.DataFrame] = None):
        self.df_movimentacoes = df_movimentacoes if df_movimentacoes is not None else pd.DataFrame()
    
    def registrar_movimentacao(self, movimentacao: Movimentacao) -> MovimentacaoResponse:
        """Registra nova movimentação com validação aprimorada"""
        try:
            # Validar tipo de movimentação
            if not movimentacao.tipo_movimentacao:
                logger.error("Tipo de movimentação não especificado")
                return MovimentacaoResponse(
                    success=False,
                    message="Tipo de movimentação é obrigatório"
                )
            
            # Gerar novo ID (converter para int Python nativo)
            novo_id = int(self.df_movimentacoes['id'].max() + 1) if not self.df_movimentacoes.empty else 1
            movimentacao.id = novo_id
            
            # Converter para dict e validar campos
            nova_movimentacao = movimentacao.dict()
            
            # Garantir que campos obrigatórios existem
            campos_obrigatorios = ['id', 'equipamento_id', 'tipo_movimentacao', 'quantidade', 'destino_origem']
            for campo in campos_obrigatorios:
                if campo not in nova_movimentacao or nova_movimentacao[campo] is None:
                    logger.error(f"Campo obrigatório '{campo}' ausente ou nulo")
                    return MovimentacaoResponse(
                        success=False,
                        message=f"Campo '{campo}' é obrigatório"
                    )
            
            # Adicionar ao DataFrame
            self.df_movimentacoes = pd.concat([
                self.df_movimentacoes, 
                pd.DataFrame([nova_movimentacao])
            ], ignore_index=True)
            
            logger.info(f"✅ Movimentação registrada com sucesso: {movimentacao.tipo_movimentacao.value} - {movimentacao.quantidade} unidades - Código: {movimentacao.codigo_produto}")
            return MovimentacaoResponse(
                success=True,
                message="Movimentação registrada com sucesso",
                movimentacao=movimentacao
            )
            
        except Exception as e:
            logger.error(f"Erro crítico ao registrar movimentação: {str(e)}")
            return MovimentacaoResponse(
                success=False,
                message=f"Erro interno: {str(e)}"
            )
    
    def obter_movimentacoes(self) -> pd.DataFrame:
        """Retorna todas as movimentações"""
        return self.df_movimentacoes.copy()
    
    def filtrar_movimentacoes(self, 
                            tipo: Optional[str] = None,
                            data_inicio: Optional[datetime] = None,
                            data_fim: Optional[datetime] = None,
                            equipamento_id: Optional[int] = None) -> pd.DataFrame:
        """Filtra movimentações por critérios"""
        df_filtrado = self.df_movimentacoes.copy()
        
        if df_filtrado.empty:
            return df_filtrado
        
        # Converter coluna de data se necessário
        if 'data_movimentacao' in df_filtrado.columns:
            df_filtrado['data_movimentacao'] = pd.to_datetime(df_filtrado['data_movimentacao'])
        
        # Filtro por tipo
        if tipo and tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado['tipo_movimentacao'] == tipo]
        
        # Filtro por data
        if data_inicio:
            df_filtrado = df_filtrado[df_filtrado['data_movimentacao'].dt.date >= data_inicio.date()]
        
        if data_fim:
            df_filtrado = df_filtrado[df_filtrado['data_movimentacao'].dt.date <= data_fim.date()]
        
        # Filtro por equipamento
        if equipamento_id:
            df_filtrado = df_filtrado[df_filtrado['equipamento_id'] == equipamento_id]
        
        return df_filtrado
    
    def obter_movimentacoes_por_equipamento(self, equipamento_id: int) -> pd.DataFrame:
        """Obtém movimentações de um equipamento específico"""
        return self.df_movimentacoes[self.df_movimentacoes['equipamento_id'] == equipamento_id].copy()
    
    def obter_estatisticas_movimentacoes(self, dias: int = 30) -> Dict[str, Any]:
        """Obtém estatísticas das movimentações"""
        try:
            if self.df_movimentacoes.empty:
                return {
                    'total_entradas': 0,
                    'total_saidas': 0,
                    'total_movimentacoes': 0,
                    'quantidade_entrada': 0,
                    'quantidade_saida': 0
                }
            
            # Filtrar por período
            data_limite = datetime.now() - timedelta(days=dias)
            df_periodo = self.df_movimentacoes.copy()
            df_periodo['data_movimentacao'] = pd.to_datetime(df_periodo['data_movimentacao'])
            df_periodo = df_periodo[df_periodo['data_movimentacao'] >= data_limite]
            
            # Calcular estatísticas
            entradas = df_periodo[df_periodo['tipo_movimentacao'] == 'Entrada']
            saidas = df_periodo[df_periodo['tipo_movimentacao'] == 'Saída']
            
            return {
                'total_entradas': len(entradas),
                'total_saidas': len(saidas),
                'total_movimentacoes': len(df_periodo),
                'quantidade_entrada': int(entradas['quantidade'].sum()) if not entradas.empty else 0,
                'quantidade_saida': int(saidas['quantidade'].sum()) if not saidas.empty else 0
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de movimentações: {str(e)}")
            return {
                'total_entradas': 0,
                'total_saidas': 0,
                'total_movimentacoes': 0,
                'quantidade_entrada': 0,
                'quantidade_saida': 0
            }
    
    def obter_movimentacoes_recentes(self, limite: int = 10) -> pd.DataFrame:
        """Obtém as movimentações mais recentes"""
        if self.df_movimentacoes.empty:
            return self.df_movimentacoes
        
        df_ordenado = self.df_movimentacoes.copy()
        df_ordenado['data_movimentacao'] = pd.to_datetime(df_ordenado['data_movimentacao'])
        return df_ordenado.sort_values('data_movimentacao', ascending=False).head(limite) 