"""
Serviço principal para lógica de negócio do estoque - Versão PostgreSQL
Migrado de Excel para PostgreSQL
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from models.schemas import (
    Equipamento, Movimentacao, EquipamentoResponse, 
    MovimentacaoResponse, StatusEquipamento, TipoMovimentacao, CondicionEquipamento
)
from services.database_service import DatabaseService
from config.settings import settings
from utils.security_utils import SecurityValidator
from utils.cache_manager import cache_equipment_data


class EstoqueService:
    """Serviço principal para gerenciar estoque com PostgreSQL"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.security_validator = SecurityValidator()
        logger.info("✅ EstoqueService inicializado com PostgreSQL")
    
    def recarregar_dados(self) -> None:
        """Recarrega dados do banco (limpa cache se necessário)"""
        # Com PostgreSQL, os dados já são sempre atualizados
        logger.info("🔄 Dados do PostgreSQL sempre atualizados")
    
    def obter_equipamentos(self) -> pd.DataFrame:
        """Retorna todos os equipamentos"""
        try:
            df = self.db_service.listar_equipamentos(apenas_ativos=True)
            
            # Renomear colunas para manter compatibilidade
            if not df.empty:
                df = df.rename(columns={
                    'Código': 'codigo_produto',
                    'Nome': 'equipamento',
                    'Categoria': 'categoria',
                    'Marca': 'marca',
                    'Modelo': 'modelo',
                    'Quantidade': 'quantidade',
                    'Condição': 'condicao',
                    'Valor Unitário': 'valor_unitario',
                    'Observações': 'observacoes',
                    'Data Cadastro': 'data_cadastro',
                    'Data Atualização': 'data_atualizacao'
                })
                
                # Calcular valor total
                df['valor_total'] = df['quantidade'] * df['valor_unitario']
                
                # Garantir que código seja string
                df['codigo_produto'] = df['codigo_produto'].astype(str)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter equipamentos: {str(e)}")
            return pd.DataFrame()
    
    def obter_equipamentos_agrupados(self) -> pd.DataFrame:
        """Retorna equipamentos agrupados por código de produto (soma Novo + Usado)"""
        df = self.obter_equipamentos()
        
        if df.empty:
            return pd.DataFrame()
        
        try:
            # Agrupar por código do produto somando quantidades
            df_agrupado = df.groupby(['codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo']).agg({
                'quantidade': 'sum',
                'valor_unitario': 'mean',  # Média do valor unitário
                'observacoes': 'first'
            }).reset_index()
            
            # Calcular valor total para cada produto agrupado
            df_agrupado['valor_total'] = df_agrupado['quantidade'] * df_agrupado['valor_unitario']
            
            return df_agrupado
            
        except Exception as e:
            logger.error(f"❌ Erro ao agrupar equipamentos: {str(e)}")
            return df.copy()
    
    def obter_equipamento_por_codigo(self, codigo: str) -> List[Dict[str, Any]]:
        """Obtém equipamentos por código (pode ter Novo e Usado)"""
        try:
            codigo_str = str(codigo).strip().upper()
            equipamentos = self.db_service.buscar_por_codigo(codigo_str)
            return equipamentos
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar equipamento por código: {str(e)}")
            return []
    
    def obter_equipamento_por_codigo_e_condicao(
        self, 
        codigo: str, 
        condicao: CondicionEquipamento
    ) -> Optional[Dict[str, Any]]:
        """Obtém equipamento específico por código e condição"""
        try:
            codigo_str = str(codigo).strip().upper()
            condicao_str = condicao.value if isinstance(condicao, CondicionEquipamento) else str(condicao)
            
            equipamento = self.db_service.buscar_equipamento(codigo_str, condicao_str)
            return equipamento
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar equipamento: {str(e)}")
            return None
    
    def adicionar_equipamento(
        self, 
        equipamento: Equipamento,
        usuario: str = "Sistema"
    ) -> EquipamentoResponse:
        """Adiciona ou atualiza equipamento no estoque"""
        try:
            # Sanitizar dados
            equipamento = self.security_validator.sanitize_equipment(equipamento)
            
            # Converter código para string uppercase
            codigo = str(equipamento.codigo_produto).strip().upper()
            
            # Verificar se já existe
            existe = self.db_service.buscar_equipamento(codigo, equipamento.condicao.value)
            
            if existe:
                # Atualizar quantidade
                nova_quantidade = existe['Quantidade'] + equipamento.quantidade
                sucesso = self.db_service.atualizar_equipamento(
                    codigo=codigo,
                    condicao=equipamento.condicao.value,
                    quantidade=nova_quantidade
                )
                
                if sucesso:
                    # Registrar movimentação
                    self.db_service.registrar_movimentacao(
                        tipo="Entrada",
                        codigo=codigo,
                        nome=equipamento.equipamento,
                        categoria=equipamento.categoria,
                        marca=equipamento.marca or "",
                        modelo=equipamento.modelo or "",
                        quantidade=equipamento.quantidade,
                        condicao=equipamento.condicao.value,
                        valor_unitario=equipamento.valor_unitario,
                        observacoes=equipamento.observacoes or "",
                        usuario=usuario
                    )
                    
                    return EquipamentoResponse(
                        success=True,
                        message=f"✅ Estoque atualizado! {equipamento.equipamento} ({equipamento.condicao.value}) - Nova quantidade: {nova_quantidade}",
                        data=None
                    )
            else:
                # Adicionar novo equipamento
                sucesso = self.db_service.adicionar_equipamento(
                    codigo=codigo,
                    nome=equipamento.equipamento,
                    categoria=equipamento.categoria,
                    marca=equipamento.marca or "",
                    modelo=equipamento.modelo or "",
                    quantidade=equipamento.quantidade,
                    condicao=equipamento.condicao.value,
                    valor_unitario=equipamento.valor_unitario,
                    observacoes=equipamento.observacoes or ""
                )
                
                if sucesso:
                    # Registrar movimentação
                    self.db_service.registrar_movimentacao(
                        tipo="Entrada",
                        codigo=codigo,
                        nome=equipamento.equipamento,
                        categoria=equipamento.categoria,
                        marca=equipamento.marca or "",
                        modelo=equipamento.modelo or "",
                        quantidade=equipamento.quantidade,
                        condicao=equipamento.condicao.value,
                        valor_unitario=equipamento.valor_unitario,
                        observacoes=equipamento.observacoes or "",
                        usuario=usuario
                    )
                    
                    return EquipamentoResponse(
                        success=True,
                        message=f"✅ Equipamento adicionado com sucesso! {equipamento.equipamento} - Código: {codigo}",
                        data=None
                    )
            
            return EquipamentoResponse(
                success=False,
                message="❌ Erro ao adicionar equipamento",
                data=None
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar equipamento: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"❌ Erro: {str(e)}",
                data=None
            )
    
    def remover_equipamento(
        self,
        codigo: str,
        condicao: CondicionEquipamento,
        quantidade_remover: int,
        usuario: str = "Sistema"
    ) -> EquipamentoResponse:
        """Remove equipamento do estoque"""
        try:
            codigo_str = str(codigo).strip().upper()
            condicao_str = condicao.value if isinstance(condicao, CondicionEquipamento) else str(condicao)
            
            # Buscar equipamento atual
            equipamento = self.db_service.buscar_equipamento(codigo_str, condicao_str)
            
            if not equipamento:
                return EquipamentoResponse(
                    success=False,
                    message=f"❌ Equipamento não encontrado: {codigo_str} ({condicao_str})",
                    data=None
                )
            
            if equipamento['Quantidade'] < quantidade_remover:
                return EquipamentoResponse(
                    success=False,
                    message=f"❌ Quantidade insuficiente. Disponível: {equipamento['Quantidade']}",
                    data=None
                )
            
            # Remover do estoque
            sucesso = self.db_service.remover_equipamento(
                codigo=codigo_str,
                condicao=condicao_str,
                quantidade_remover=quantidade_remover
            )
            
            if sucesso:
                # Registrar movimentação
                self.db_service.registrar_movimentacao(
                    tipo="Saída",
                    codigo=codigo_str,
                    nome=equipamento['Nome'],
                    categoria=equipamento['Categoria'],
                    marca=equipamento.get('Marca', ''),
                    modelo=equipamento.get('Modelo', ''),
                    quantidade=quantidade_remover,
                    condicao=condicao_str,
                    valor_unitario=equipamento.get('Valor Unitário', 0),
                    observacoes="",
                    usuario=usuario
                )
                
                nova_qtd = equipamento['Quantidade'] - quantidade_remover
                return EquipamentoResponse(
                    success=True,
                    message=f"✅ Equipamento removido! Quantidade restante: {nova_qtd}",
                    data=None
                )
            
            return EquipamentoResponse(
                success=False,
                message="❌ Erro ao remover equipamento",
                data=None
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover equipamento: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"❌ Erro: {str(e)}",
                data=None
            )
    
    def gerar_codigo_automatico(self, categoria: str) -> str:
        """Gera código automático baseado na categoria"""
        try:
            prefixo = settings.PREFIXOS_CODIGO.get(categoria, "PRD")
            
            # Buscar maior código existente com esse prefixo
            df = self.obter_equipamentos()
            
            if df.empty:
                return f"{prefixo}001"
            
            codigos_prefixo = df[df['codigo_produto'].str.startswith(prefixo)]['codigo_produto'].tolist()
            
            if not codigos_prefixo:
                return f"{prefixo}001"
            
            # Extrair números e encontrar o maior
            numeros = []
            for cod in codigos_prefixo:
                try:
                    num = int(cod.replace(prefixo, ''))
                    numeros.append(num)
                except:
                    continue
            
            if numeros:
                proximo = max(numeros) + 1
            else:
                proximo = 1
            
            return f"{prefixo}{proximo:03d}"
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar código: {str(e)}")
            return "PRD001"
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do estoque"""
        try:
            stats = self.db_service.obter_estatisticas()
            return stats
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {
                'total_equipamentos': 0,
                'por_categoria': {},
                'por_condicao': {},
                'valor_total': 0
            }
    
    def obter_movimentacoes(
        self, 
        dias: Optional[int] = None
    ) -> pd.DataFrame:
        """Obtém movimentações"""
        try:
            df = self.db_service.listar_movimentacoes(dias=dias)
            return df
        except Exception as e:
            logger.error(f"❌ Erro ao obter movimentações: {str(e)}")
            return pd.DataFrame()
    
    def codigo_existe(self, codigo: str) -> bool:
        """Verifica se código já existe"""
        try:
            codigo_str = str(codigo).strip().upper()
            return self.db_service.codigo_existe(codigo_str)
        except:
            return False

