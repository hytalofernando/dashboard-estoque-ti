"""
Serviço principal para lógica de negócio do estoque
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from models.schemas import Equipamento, Movimentacao, EquipamentoResponse, MovimentacaoResponse, StatusEquipamento, TipoMovimentacao
from services.excel_service import ExcelService
from services.movimentacao_service import MovimentacaoService
from config.settings import settings
from utils.security_utils import SecurityValidator
from utils.cache_manager import cache_equipment_data

class EstoqueService:
    """Serviço principal para gerenciar estoque"""
    
    def __init__(self):
        self.excel_service = ExcelService()
        self.df_estoque, self.df_movimentacoes = self.excel_service.carregar_dados()
        self.movimentacao_service = MovimentacaoService(self.df_movimentacoes)
        self.security_validator = SecurityValidator()
    
    def recarregar_dados(self) -> None:
        """Recarrega dados do Excel"""
        self.df_estoque, self.df_movimentacoes = self.excel_service.carregar_dados()
        self.movimentacao_service.df_movimentacoes = self.df_movimentacoes
    
    def obter_equipamentos(self) -> pd.DataFrame:
        """Retorna todos os equipamentos"""
        return self.df_estoque.copy()
    
    def obter_equipamento_por_id(self, equipamento_id: int) -> Optional[pd.Series]:
        """Obtém equipamento por ID"""
        equipamentos = self.df_estoque[self.df_estoque['id'] == equipamento_id]
        return equipamentos.iloc[0] if not equipamentos.empty else None
    
    def obter_equipamento_por_codigo(self, codigo: str) -> Optional[pd.Series]:
        """Obtém equipamento por código"""
        equipamentos = self.df_estoque[self.df_estoque['codigo_produto'] == codigo.upper()]
        return equipamentos.iloc[0] if not equipamentos.empty else None
    
    def codigo_existe(self, codigo: str, excluir_id: Optional[int] = None) -> bool:
        """Verifica se código já existe"""
        df_filtrado = self.df_estoque[self.df_estoque['codigo_produto'] == codigo.upper()]
        if excluir_id:
            df_filtrado = df_filtrado[df_filtrado['id'] != excluir_id]
        return not df_filtrado.empty
    
    def gerar_codigo_sugerido(self, categoria: str, marca: str) -> str:
        """Gera código sugerido baseado na categoria e marca"""
        prefixo = settings.PREFIXOS_CODIGO.get(categoria, 'OUT')
        equipamentos_similares = self.df_estoque[
            (self.df_estoque['categoria'] == categoria) & 
            (self.df_estoque['marca'] == marca)
        ]
        numero = len(equipamentos_similares) + 1
        return f"{prefixo}-{marca.upper()}-{numero:03d}"
    
    def adicionar_equipamento(self, equipamento: Equipamento) -> EquipamentoResponse:
        """Adiciona novo equipamento ao estoque com validações de segurança"""
        try:
            # ✅ SANITIZAR E VALIDAR DADOS DE ENTRADA
            equipamento_data = self.security_validator.validate_equipment_data(equipamento.dict())
            
            # Recriar objeto Equipamento com dados sanitizados
            equipamento_sanitized = Equipamento(**equipamento_data)
            
            # Verificar se código já existe
            if self.codigo_existe(equipamento_sanitized.codigo_produto):
                logger.warning(f"🚨 Tentativa de adicionar código duplicado: {equipamento_sanitized.codigo_produto}")
                return EquipamentoResponse(
                    success=False,
                    message=f"Código '{equipamento_sanitized.codigo_produto}' já existe"
                )
            
            # Gerar novo ID (converter para int Python nativo)
            novo_id = int(self.df_estoque['id'].max() + 1) if not self.df_estoque.empty else 1
            equipamento_sanitized.id = novo_id
            
            # Adicionar ao DataFrame com dados sanitizados
            novo_equipamento = equipamento_sanitized.dict()
            self.df_estoque = pd.concat([
                self.df_estoque, 
                pd.DataFrame([novo_equipamento])
            ], ignore_index=True)
            
            # Registrar movimentação de entrada
            movimentacao = Movimentacao(
                equipamento_id=novo_id,
                tipo_movimentacao=TipoMovimentacao.ENTRADA,
                quantidade=equipamento_sanitized.quantidade,
                destino_origem=f"Fornecedor: {equipamento_sanitized.fornecedor}",
                observacoes=f"Adição inicial ao estoque | Código: {equipamento_sanitized.codigo_produto}",
                codigo_produto=equipamento_sanitized.codigo_produto
            )
            
            self.movimentacao_service.registrar_movimentacao(movimentacao)
            self.df_movimentacoes = self.movimentacao_service.df_movimentacoes
            
            # Salvar dados
            if self.excel_service.salvar_dados(self.df_estoque, self.df_movimentacoes):
                logger.info(f"✅ Equipamento adicionado com segurança: {equipamento_sanitized.codigo_produto}")
                return EquipamentoResponse(
                    success=True,
                    message=f"Equipamento '{equipamento_sanitized.equipamento}' adicionado com sucesso!",
                    equipamento=equipamento_sanitized.dict()
                )
            else:
                return EquipamentoResponse(
                    success=False,
                    message="Erro ao salvar dados"
                )
                
        except Exception as e:
            logger.error(f"Erro ao adicionar equipamento: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"Erro interno: {str(e)}"
            )
    
    def aumentar_estoque(self, equipamento_id: int, quantidade: int, valor_unitario: float, fornecedor: str) -> EquipamentoResponse:
        """Aumenta o estoque de um equipamento existente"""
        try:
            equipamento = self.obter_equipamento_por_id(equipamento_id)
            if equipamento is None:
                return EquipamentoResponse(
                    success=False,
                    message="Equipamento não encontrado"
                )
            
            # ✅ VALIDAÇÃO DE TIPOS
            if not isinstance(valor_unitario, (int, float)):
                valor_unitario = float(equipamento['valor_unitario']) if 'valor_unitario' in equipamento else 0.0
                logger.warning(f"valor_unitario inválido, usando valor original: {valor_unitario}")
            
            if not isinstance(fornecedor, str):
                fornecedor = str(fornecedor) if fornecedor else "Fornecedor Padrão"
            
            idx = self.df_estoque[self.df_estoque['id'] == equipamento_id].index[0]
            nova_quantidade = equipamento['quantidade'] + quantidade
            
            if nova_quantidade > settings.MAX_QUANTIDADE:
                return EquipamentoResponse(
                    success=False,
                    message=f"Quantidade total excederia o limite de {settings.MAX_QUANTIDADE}"
                )
            
            # Atualizar equipamento com tipos garantidos
            self.df_estoque.loc[idx, 'quantidade'] = int(nova_quantidade)
            self.df_estoque.loc[idx, 'valor_unitario'] = float(valor_unitario)
            self.df_estoque.loc[idx, 'fornecedor'] = str(fornecedor)
            self.df_estoque.loc[idx, 'status'] = "Disponível"  # ✅ String simples em vez de StatusEquipamento.DISPONIVEL
            
            # Registrar movimentação
            movimentacao = Movimentacao(
                equipamento_id=equipamento_id,
                tipo_movimentacao=TipoMovimentacao.ENTRADA,
                quantidade=quantidade,
                destino_origem=f"Fornecedor: {fornecedor}",
                observacoes=f"Aumento de estoque | Código: {equipamento['codigo_produto']}",
                codigo_produto=equipamento['codigo_produto']
            )
            
            self.movimentacao_service.registrar_movimentacao(movimentacao)
            self.df_movimentacoes = self.movimentacao_service.df_movimentacoes
            
            # Salvar dados
            if self.excel_service.salvar_dados(self.df_estoque, self.df_movimentacoes):
                logger.info(f"Estoque aumentado: {equipamento['codigo_produto']} +{quantidade}")
                return EquipamentoResponse(
                    success=True,
                    message=f"Estoque aumentado com sucesso! Nova quantidade: {nova_quantidade}",
                    nova_quantidade=int(nova_quantidade)
                )
            else:
                return EquipamentoResponse(
                    success=False,
                    message="Erro ao salvar dados"
                )
                
        except Exception as e:
            logger.error(f"Erro ao aumentar estoque: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"Erro interno: {str(e)}"
            )
    
    def remover_equipamento(self, equipamento_id: int, quantidade: int, destino: str, observacoes: str = "") -> EquipamentoResponse:
        """Remove equipamento do estoque"""
        try:
            equipamento = self.obter_equipamento_por_id(equipamento_id)
            if equipamento is None:
                return EquipamentoResponse(
                    success=False,
                    message="Equipamento não encontrado"
                )
            
            if equipamento['quantidade'] < quantidade:
                return EquipamentoResponse(
                    success=False,
                    message=f"Quantidade insuficiente. Disponível: {equipamento['quantidade']}"
                )
            
            idx = self.df_estoque[self.df_estoque['id'] == equipamento_id].index[0]
            nova_quantidade = equipamento['quantidade'] - quantidade
            
            # Atualizar quantidade (converter para int Python nativo)
            self.df_estoque.loc[idx, 'quantidade'] = int(nova_quantidade)
            
            # Atualizar status se necessário
            if nova_quantidade == 0:
                self.df_estoque.loc[idx, 'status'] = "Indisponível"  # ✅ String simples em vez de StatusEquipamento.INDISPONIVEL
            
            # Registrar movimentação
            observacoes_completas = f"{observacoes} | Código: {equipamento['codigo_produto']}" if observacoes else f"Código: {equipamento['codigo_produto']}"
            
            movimentacao = Movimentacao(
                equipamento_id=equipamento_id,
                tipo_movimentacao=TipoMovimentacao.SAIDA,
                quantidade=quantidade,
                destino_origem=destino,
                observacoes=observacoes_completas,
                codigo_produto=equipamento['codigo_produto']
            )
            
            self.movimentacao_service.registrar_movimentacao(movimentacao)
            self.df_movimentacoes = self.movimentacao_service.df_movimentacoes
            
            # Salvar dados
            if self.excel_service.salvar_dados(self.df_estoque, self.df_movimentacoes):
                valor_total = quantidade * equipamento['valor_unitario']
                logger.info(f"Equipamento removido: {equipamento['codigo_produto']} -{quantidade}")
                return EquipamentoResponse(
                    success=True,
                    message=f"Equipamento removido com sucesso! Quantidade: {quantidade}, Valor: R$ {valor_total:,.2f}",
                    nova_quantidade=int(nova_quantidade)
                )
            else:
                return EquipamentoResponse(
                    success=False,
                    message="Erro ao salvar dados"
                )
                
        except Exception as e:
            logger.error(f"Erro ao remover equipamento: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"Erro interno: {str(e)}"
            )
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do estoque"""
        try:
            total_equipamentos = self.df_estoque['quantidade'].sum()
            valor_total = (self.df_estoque['quantidade'] * self.df_estoque['valor_unitario']).sum()
            categorias_unicas = self.df_estoque['categoria'].nunique()
            disponiveis = self.df_estoque[self.df_estoque['status'] == StatusEquipamento.DISPONIVEL]['quantidade'].sum()
            
            return {
                'total_equipamentos': int(total_equipamentos),
                'valor_total': float(valor_total),
                'categorias_unicas': int(categorias_unicas),
                'disponiveis': int(disponiveis),
                'total_tipos': len(self.df_estoque),
                'em_manutencao': len(self.df_estoque[self.df_estoque['status'] == StatusEquipamento.MANUTENCAO])
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'total_equipamentos': 0,
                'valor_total': 0.0,
                'categorias_unicas': 0,
                'disponiveis': 0,
                'total_tipos': 0,
                'em_manutencao': 0
            }
    
    def filtrar_equipamentos(self, categoria: Optional[str] = None, marca: Optional[str] = None, status: Optional[str] = None, codigo: Optional[str] = None) -> pd.DataFrame:
        """Filtra equipamentos por critérios"""
        df_filtrado = self.df_estoque.copy()
        
        if categoria and categoria != "Todas":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]
        
        if marca and marca != "Todas":
            df_filtrado = df_filtrado[df_filtrado['marca'] == marca]
        
        if status and status != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == status]
        
        if codigo:
            df_filtrado = df_filtrado[
                (df_filtrado['codigo_produto'].str.contains(codigo, case=False, na=False)) |
                (df_filtrado['equipamento'].str.contains(codigo, case=False, na=False))
            ]
        
        return df_filtrado 