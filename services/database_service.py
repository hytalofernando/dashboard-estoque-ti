"""
Serviço de Banco de Dados - Dashboard Estoque TI
Operações CRUD para PostgreSQL
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from models.database_models import (
    Equipamento, 
    Movimentacao, 
    db_connection
)


class DatabaseService:
    """Serviço para operações no banco de dados"""
    
    def __init__(self):
        self.db = db_connection
        logger.info("🗄️ DatabaseService inicializado")
    
    # ==================== EQUIPAMENTOS ====================
    
    def adicionar_equipamento(
        self,
        codigo: str,
        nome: str,
        categoria: str,
        marca: str,
        modelo: str,
        quantidade: int,
        condicao: str,
        valor_unitario: float,
        observacoes: str = ""
    ) -> bool:
        """
        Adiciona um novo equipamento ao banco
        
        Returns:
            True se adicionado com sucesso
        """
        session = self.db.get_session()
        try:
            equipamento = Equipamento(
                codigo=codigo,
                nome=nome,
                categoria=categoria,
                marca=marca,
                modelo=modelo,
                quantidade=quantidade,
                condicao=condicao,
                valor_unitario=valor_unitario,
                observacoes=observacoes
            )
            
            session.add(equipamento)
            session.commit()
            
            logger.info(f"✅ Equipamento adicionado: {codigo} - {nome}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"❌ Erro ao adicionar equipamento: {str(e)}")
            return False
        finally:
            session.close()
    
    def atualizar_equipamento(
        self,
        codigo: str,
        condicao: str,
        quantidade: int
    ) -> bool:
        """
        Atualiza a quantidade de um equipamento existente
        
        Returns:
            True se atualizado com sucesso
        """
        session = self.db.get_session()
        try:
            equipamento = session.query(Equipamento).filter(
                and_(
                    Equipamento.codigo == codigo,
                    Equipamento.condicao == condicao,
                    Equipamento.ativo == True
                )
            ).first()
            
            if equipamento:
                equipamento.quantidade = quantidade
                equipamento.data_atualizacao = datetime.now()
                session.commit()
                logger.info(f"✅ Equipamento atualizado: {codigo} ({condicao}) - Qtd: {quantidade}")
                return True
            else:
                logger.warning(f"⚠️ Equipamento não encontrado: {codigo} ({condicao})")
                return False
                
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"❌ Erro ao atualizar equipamento: {str(e)}")
            return False
        finally:
            session.close()
    
    def remover_equipamento(
        self,
        codigo: str,
        condicao: str,
        quantidade_remover: int
    ) -> bool:
        """
        Remove quantidade de um equipamento ou marca como inativo se quantidade = 0
        
        Returns:
            True se removido com sucesso
        """
        session = self.db.get_session()
        try:
            equipamento = session.query(Equipamento).filter(
                and_(
                    Equipamento.codigo == codigo,
                    Equipamento.condicao == condicao,
                    Equipamento.ativo == True
                )
            ).first()
            
            if not equipamento:
                logger.warning(f"⚠️ Equipamento não encontrado: {codigo} ({condicao})")
                return False
            
            nova_quantidade = equipamento.quantidade - quantidade_remover
            
            if nova_quantidade <= 0:
                # Marcar como inativo
                equipamento.ativo = False
                equipamento.quantidade = 0
                logger.info(f"🗑️ Equipamento marcado como inativo: {codigo} ({condicao})")
            else:
                equipamento.quantidade = nova_quantidade
                logger.info(f"➖ Quantidade removida: {codigo} ({condicao}) - Nova qtd: {nova_quantidade}")
            
            equipamento.data_atualizacao = datetime.now()
            session.commit()
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"❌ Erro ao remover equipamento: {str(e)}")
            return False
        finally:
            session.close()
    
    def buscar_equipamento(
        self,
        codigo: str,
        condicao: str
    ) -> Optional[Dict[str, Any]]:
        """
        Busca um equipamento específico
        
        Returns:
            Dicionário com dados do equipamento ou None
        """
        session = self.db.get_session()
        try:
            equipamento = session.query(Equipamento).filter(
                and_(
                    Equipamento.codigo == codigo,
                    Equipamento.condicao == condicao,
                    Equipamento.ativo == True
                )
            ).first()
            
            if equipamento:
                return equipamento.to_dict()
            return None
            
        finally:
            session.close()
    
    def listar_equipamentos(self, apenas_ativos: bool = True) -> pd.DataFrame:
        """
        Lista todos os equipamentos
        
        Returns:
            DataFrame com todos os equipamentos
        """
        session = self.db.get_session()
        try:
            query = session.query(Equipamento)
            
            if apenas_ativos:
                query = query.filter(Equipamento.ativo == True)
            
            equipamentos = query.order_by(Equipamento.codigo).all()
            
            if not equipamentos:
                return pd.DataFrame()
            
            # Converter para DataFrame
            data = [eq.to_dict() for eq in equipamentos]
            df = pd.DataFrame(data)
            
            # Remover colunas internas
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
            if 'Ativo' in df.columns and apenas_ativos:
                df = df.drop(columns=['Ativo'])
            
            return df
            
        finally:
            session.close()
    
    def buscar_por_codigo(self, codigo: str) -> List[Dict[str, Any]]:
        """
        Busca todos os equipamentos com determinado código
        
        Returns:
            Lista de equipamentos (diferentes condições)
        """
        session = self.db.get_session()
        try:
            equipamentos = session.query(Equipamento).filter(
                and_(
                    Equipamento.codigo == codigo,
                    Equipamento.ativo == True
                )
            ).all()
            
            return [eq.to_dict() for eq in equipamentos]
            
        finally:
            session.close()
    
    # ==================== MOVIMENTAÇÕES ====================
    
    def registrar_movimentacao(
        self,
        tipo: str,
        codigo: str,
        nome: str,
        categoria: str,
        marca: str,
        modelo: str,
        quantidade: int,
        condicao: str,
        valor_unitario: float,
        observacoes: str = "",
        usuario: str = "Sistema"
    ) -> bool:
        """
        Registra uma movimentação (entrada ou saída)
        
        Returns:
            True se registrado com sucesso
        """
        session = self.db.get_session()
        try:
            movimentacao = Movimentacao(
                tipo=tipo,
                codigo=codigo,
                nome=nome,
                categoria=categoria,
                marca=marca,
                modelo=modelo,
                quantidade=quantidade,
                condicao=condicao,
                valor_unitario=valor_unitario,
                observacoes=observacoes,
                usuario=usuario
            )
            
            session.add(movimentacao)
            session.commit()
            
            logger.info(f"📝 Movimentação registrada: {tipo} - {codigo} - Qtd: {quantidade}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"❌ Erro ao registrar movimentação: {str(e)}")
            return False
        finally:
            session.close()
    
    def listar_movimentacoes(
        self,
        dias: Optional[int] = None,
        tipo: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Lista movimentações com filtros opcionais
        
        Args:
            dias: Número de dias para filtrar (None = todas)
            tipo: Tipo de movimentação (None = todas)
        
        Returns:
            DataFrame com movimentações
        """
        session = self.db.get_session()
        try:
            query = session.query(Movimentacao)
            
            # Filtro por período
            if dias:
                data_limite = datetime.now() - timedelta(days=dias)
                query = query.filter(Movimentacao.data_movimentacao >= data_limite)
            
            # Filtro por tipo
            if tipo:
                query = query.filter(Movimentacao.tipo == tipo)
            
            movimentacoes = query.order_by(
                Movimentacao.data_movimentacao.desc()
            ).all()
            
            if not movimentacoes:
                return pd.DataFrame()
            
            # Converter para DataFrame
            data = [mov.to_dict() for mov in movimentacoes]
            df = pd.DataFrame(data)
            
            # Remover coluna id
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
            
            return df
            
        finally:
            session.close()
    
    def obter_movimentacoes_por_periodo(
        self,
        data_inicio: datetime,
        data_fim: datetime
    ) -> pd.DataFrame:
        """
        Obtém movimentações em um período específico
        
        Returns:
            DataFrame com movimentações do período
        """
        session = self.db.get_session()
        try:
            movimentacoes = session.query(Movimentacao).filter(
                and_(
                    Movimentacao.data_movimentacao >= data_inicio,
                    Movimentacao.data_movimentacao <= data_fim
                )
            ).order_by(Movimentacao.data_movimentacao.desc()).all()
            
            if not movimentacoes:
                return pd.DataFrame()
            
            data = [mov.to_dict() for mov in movimentacoes]
            df = pd.DataFrame(data)
            
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
            
            return df
            
        finally:
            session.close()
    
    # ==================== ESTATÍSTICAS ====================
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais do estoque
        
        Returns:
            Dicionário com estatísticas
        """
        session = self.db.get_session()
        try:
            # Total de equipamentos
            total_equipamentos = session.query(
                func.sum(Equipamento.quantidade)
            ).filter(Equipamento.ativo == True).scalar() or 0
            
            # Total por categoria
            por_categoria = session.query(
                Equipamento.categoria,
                func.sum(Equipamento.quantidade).label('total')
            ).filter(Equipamento.ativo == True).group_by(
                Equipamento.categoria
            ).all()
            
            # Total por condição
            por_condicao = session.query(
                Equipamento.condicao,
                func.sum(Equipamento.quantidade).label('total')
            ).filter(Equipamento.ativo == True).group_by(
                Equipamento.condicao
            ).all()
            
            # Valor total do estoque
            valor_total = session.query(
                func.sum(Equipamento.quantidade * Equipamento.valor_unitario)
            ).filter(Equipamento.ativo == True).scalar() or 0
            
            return {
                'total_equipamentos': int(total_equipamentos),
                'por_categoria': {cat: int(total) for cat, total in por_categoria},
                'por_condicao': {cond: int(total) for cond, total in por_condicao},
                'valor_total': float(valor_total)
            }
            
        finally:
            session.close()
    
    # ==================== UTILITÁRIOS ====================
    
    def codigo_existe(self, codigo: str) -> bool:
        """Verifica se um código já existe no banco"""
        session = self.db.get_session()
        try:
            existe = session.query(Equipamento).filter(
                and_(
                    Equipamento.codigo == codigo,
                    Equipamento.ativo == True
                )
            ).first() is not None
            
            return existe
            
        finally:
            session.close()
    
    def limpar_banco(self) -> bool:
        """CUIDADO: Limpa todos os dados do banco (apenas para desenvolvimento)"""
        session = self.db.get_session()
        try:
            session.query(Movimentacao).delete()
            session.query(Equipamento).delete()
            session.commit()
            logger.warning("⚠️ Banco de dados limpo!")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"❌ Erro ao limpar banco: {str(e)}")
            return False
        finally:
            session.close()

