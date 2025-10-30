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
        # Criar um objeto simples para compatibilidade com histórico
        self.movimentacao_service = self._create_movimentacao_adapter()
        logger.info("✅ EstoqueService inicializado com PostgreSQL")
    
    def _create_movimentacao_adapter(self):
        """Cria adapter para movimentações para compatibilidade com páginas"""
        class MovimentacaoAdapter:
            def __init__(self, db_service):
                self.db_service = db_service
            
            def obter_movimentacoes(self, dias=None):
                return self.db_service.listar_movimentacoes(dias=dias)
        
        return MovimentacaoAdapter(self.db_service)
    
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
    
    def agrupar_equipamentos_por_codigo(self, codigo: str) -> Dict[str, Any]:
        """Agrupa equipamentos por código mostrando totais de Novo e Usado"""
        try:
            codigo_str = str(codigo).strip().upper()
            equipamentos = self.obter_equipamento_por_codigo(codigo_str)
            
            if not equipamentos:
                return {}
            
            resultado = {
                'codigo_produto': codigo_str,
                'equipamento': equipamentos[0].get('Nome', ''),
                'categoria': equipamentos[0].get('Categoria', ''),
                'marca': equipamentos[0].get('Marca', ''),
                'modelo': equipamentos[0].get('Modelo', ''),
                'qtd_novos': 0,
                'qtd_usados': 0,
                'valor_novos': 0.0,
                'valor_usados': 0.0,
                'fornecedor': ''
            }
            
            for eq in equipamentos:
                condicao_raw = eq.get('Condição', 'Novo')
                quantidade = eq.get('Quantidade', 0)
                valor = eq.get('Valor Unitário', 0.0)
                
                # Normalizar condição
                if 'NOVO' in str(condicao_raw).upper() or condicao_raw == CondicionEquipamento.NOVO.value:
                    resultado['qtd_novos'] = quantidade
                    resultado['valor_novos'] = valor
                elif 'USADO' in str(condicao_raw).upper() or condicao_raw == CondicionEquipamento.USADO.value:
                    resultado['qtd_usados'] = quantidade
                    resultado['valor_usados'] = valor
            
            resultado['qtd_total'] = resultado['qtd_novos'] + resultado['qtd_usados']
            resultado['valor_medio'] = (
                (resultado['qtd_novos'] * resultado['valor_novos'] + 
                 resultado['qtd_usados'] * resultado['valor_usados']) / 
                resultado['qtd_total'] if resultado['qtd_total'] > 0 else 0
            )
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao agrupar equipamentos: {str(e)}")
            return {}
    
    def aumentar_estoque(
        self, 
        equipamento_id: int, 
        quantidade: int, 
        valor_unitario: float, 
        fornecedor: str,
        condicao: Optional[CondicionEquipamento] = None,
        usuario: str = "Sistema"
    ) -> EquipamentoResponse:
        """Aumenta o estoque de um equipamento existente"""
        try:
            # Buscar equipamento pelo ID não é possível direto no database_service
            # Vamos usar uma abordagem diferente: buscar todos e filtrar
            df_equipamentos = self.obter_equipamentos()
            
            if df_equipamentos.empty:
                return EquipamentoResponse(
                    success=False,
                    message="Nenhum equipamento encontrado",
                    data=None
                )
            
            # Filtrar pelo código (já que o adicionar_page passa o id que na verdade é o código)
            # Na página de adicionar, o 'id' vem do cache que na verdade armazena o código
            # Precisamos adaptar para usar código + condição
            return EquipamentoResponse(
                success=False,
                message="Use adicionar_equipamento para aumentar estoque",
                data=None
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao aumentar estoque: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"❌ Erro: {str(e)}",
                data=None
            )
    
    def adicionar_equipamento(
        self, 
        equipamento: Equipamento,
        usuario: str = "Sistema"
    ) -> EquipamentoResponse:
        """Adiciona ou atualiza equipamento no estoque"""
        try:
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
                        observacoes=getattr(equipamento, 'observacoes', '') or "",
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
                    observacoes=getattr(equipamento, 'observacoes', '') or ""
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
                        observacoes=getattr(equipamento, 'observacoes', '') or "",
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
    
    def _normalizar_condicao(self, condicao_raw) -> str:
        """Normaliza condição para formato padrão (Novo/Usado)"""
        if not condicao_raw or condicao_raw == 'N/A':
            return 'N/A'

        # Se já for um valor válido, retornar como está
        if condicao_raw in [CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value]:
            return condicao_raw

        # Se for string com formato "CondicionEquipamento.XYZ", extrair o valor
        condicao_str = str(condicao_raw)
        if 'CondicionEquipamento.' in condicao_str:
            if 'NOVO' in condicao_str:
                return CondicionEquipamento.NOVO.value
            elif 'USADO' in condicao_str:
                return CondicionEquipamento.USADO.value

        # Se for apenas "NOVO" ou "USADO" maiúsculo
        if condicao_str.upper() == 'NOVO':
            return CondicionEquipamento.NOVO.value
        elif condicao_str.upper() == 'USADO':
            return CondicionEquipamento.USADO.value

        return condicao_raw
    
    def gerar_codigo_sugerido(self, categoria: str, marca: str) -> str:
        """Gera código sugerido baseado na categoria e marca"""
        from config.settings import settings
        
        prefixo = settings.PREFIXOS_CODIGO.get(categoria, 'OUT')
        
        # Buscar equipamentos similares
        df_estoque = self.obter_equipamentos()
        if df_estoque.empty:
            return f"{prefixo}-{marca.upper()}-001"
        
        equipamentos_similares = df_estoque[
            (df_estoque['categoria'] == categoria) & 
            (df_estoque['marca'] == marca)
        ]
        numero = len(equipamentos_similares) + 1
        return f"{prefixo}-{marca.upper()}-{numero:03d}"
    
    def remover_equipamento(
        self,
        equipamento_id_ou_codigo: Any,
        quantidade_remover: int,
        destino: str = "",
        observacoes: str = "",
        condicao: Optional[CondicionEquipamento] = None,
        usuario: str = "Sistema"
    ) -> EquipamentoResponse:
        """Remove equipamento do estoque - Compatível com páginas"""
        try:
            # O equipamento_id_ou_codigo na verdade é o código do produto
            codigo_str = str(equipamento_id_ou_codigo).strip().upper()
            
            # Se não tiver condição, tentar descobrir
            if condicao is None:
                condicao = CondicionEquipamento.NOVO  # Padrão
            
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
            
            # Preparar observações completas incluindo destino
            obs_completas = f"Destino: {destino}"
            if observacoes:
                obs_completas += f" | {observacoes}"
            
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
                    observacoes=obs_completas,
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
        """Obtém estatísticas do estoque com normalização de condições"""
        try:
            stats = self.db_service.obter_estatisticas()
            
            # Normalizar condições para formato esperado pelo dashboard
            por_condicao_normalizado = {}
            total_novos = 0
            total_usados = 0
            valor_novos = 0.0
            valor_usados = 0.0
            
            for condicao, quantidade in stats.get('por_condicao', {}).items():
                condicao_norm = self._normalizar_condicao(condicao)
                if condicao_norm == 'Novo':
                    total_novos += quantidade
                elif condicao_norm == 'Usado':
                    total_usados += quantidade
            
            # Calcular valor por condição buscando do DataFrame
            try:
                df = self.obter_equipamentos()
                if not df.empty and 'condicao' in df.columns:
                    for _, row in df.iterrows():
                        condicao_norm = self._normalizar_condicao(row.get('condicao', ''))
                        valor_item = row.get('quantidade', 0) * row.get('valor_unitario', 0)
                        if condicao_norm == 'Novo':
                            valor_novos += valor_item
                        elif condicao_norm == 'Usado':
                            valor_usados += valor_item
            except Exception as e:
                logger.warning(f"Erro ao calcular valores por condição: {str(e)}")
            
            # Adicionar estatísticas calculadas
            stats['total_novos'] = total_novos
            stats['total_usados'] = total_usados
            stats['valor_novos'] = valor_novos
            stats['valor_usados'] = valor_usados
            stats['percentual_novos'] = (total_novos / stats['total_equipamentos'] * 100) if stats['total_equipamentos'] > 0 else 0
            
            # Adicionar métricas de performance (simuladas por enquanto)
            stats['rotatividade_30d'] = 5.2  # TODO: calcular do histórico
            stats['rotatividade_7d'] = 1.8   # TODO: calcular do histórico
            stats['categorias_unicas'] = len(stats.get('por_categoria', {}))
            
            return stats
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {
                'total_equipamentos': 0,
                'por_categoria': {},
                'por_condicao': {},
                'valor_total': 0,
                'total_novos': 0,
                'total_usados': 0,
                'valor_novos': 0.0,
                'valor_usados': 0.0,
                'percentual_novos': 0,
                'rotatividade_30d': 0,
                'rotatividade_7d': 0,
                'categorias_unicas': 0
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

