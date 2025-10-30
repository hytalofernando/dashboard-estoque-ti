"""
Serviço principal para lógica de negócio do estoque
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from models.schemas import Equipamento, Movimentacao, EquipamentoResponse, MovimentacaoResponse, StatusEquipamento, TipoMovimentacao, CondicionEquipamento
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
    
    def obter_equipamentos_agrupados(self) -> pd.DataFrame:
        """Retorna equipamentos agrupados por código de produto (soma Novo + Usado)"""
        if self.df_estoque.empty:
            return pd.DataFrame()
        
        try:
            # Agrupar por código do produto somando quantidades
            df_agrupado = self.df_estoque.groupby(['codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo']).agg({
                'quantidade': 'sum',
                'valor_unitario': 'mean',  # Usar média do valor unitário para o mesmo produto
                'status': 'first',  # Pegar o primeiro status
                'fornecedor': 'first',  # Pegar o primeiro fornecedor
                'data_chegada': 'first'  # Pegar a primeira data de chegada
            }).reset_index()
            
            # Calcular valor total para cada produto agrupado
            df_agrupado['valor_total'] = df_agrupado['quantidade'] * df_agrupado['valor_unitario']
            
            return df_agrupado
            
        except Exception as e:
            logger.error(f"Erro ao agrupar equipamentos: {str(e)}")
            return self.df_estoque.copy()
    
    def obter_equipamento_por_id(self, equipamento_id: int) -> Optional[pd.Series]:
        """Obtém equipamento por ID"""
        equipamentos = self.df_estoque[self.df_estoque['id'] == equipamento_id]
        return equipamentos.iloc[0] if not equipamentos.empty else None
    
    def obter_equipamento_por_codigo(self, codigo) -> List[pd.Series]:
        """Obtém equipamentos por código (pode ter Novo e Usado)"""
        # Converter código para o mesmo tipo da coluna para comparação correta
        if isinstance(codigo, str):
            # Se for string, tentar converter para o tipo da coluna
            try:
                if self.df_estoque['codigo_produto'].dtype in ['int64', 'float64']:
                    # Para tipos numéricos, converter para float (mais seguro)
                    codigo_comparacao = float(codigo)
                else:
                    codigo_comparacao = codigo.upper()
            except ValueError:
                # Se não conseguir converter, manter como string
                codigo_comparacao = codigo.upper()
        else:
            # Se já for numérico, usar diretamente
            codigo_comparacao = codigo

        equipamentos = self.df_estoque[self.df_estoque['codigo_produto'] == codigo_comparacao]
        return [equipamentos.iloc[i] for i in range(len(equipamentos))] if not equipamentos.empty else []
    
    def obter_equipamento_por_codigo_e_condicao(self, codigo, condicao: CondicionEquipamento) -> Optional[pd.Series]:
        """Obtém equipamento específico por código e condição"""
        # Converter código para o mesmo tipo da coluna para comparação correta
        if isinstance(codigo, str):
            try:
                if self.df_estoque['codigo_produto'].dtype in ['int64', 'float64']:
                    # Para tipos numéricos, converter para float (mais seguro)
                    codigo_comparacao = float(codigo)
                else:
                    codigo_comparacao = codigo.upper()
            except ValueError:
                codigo_comparacao = codigo.upper()
        else:
            codigo_comparacao = codigo

        # Criar filtro considerando possíveis formatos da condição
        df_filtrado = self.df_estoque[self.df_estoque['codigo_produto'] == codigo_comparacao]

        # Aplicar filtro de condição com normalização
        equipamentos_filtrados = []
        for idx, row in df_filtrado.iterrows():
            condicao_normalizada = self._normalizar_condicao(row['condicao'])
            if condicao_normalizada == condicao.value:
                equipamentos_filtrados.append(row)

        if equipamentos_filtrados:
            # Converter Series do pandas para dicionário
            equipamento_dict = equipamentos_filtrados[0].to_dict()
            return equipamento_dict
        return None
    
    def agrupar_equipamentos_por_codigo(self, codigo) -> Dict[str, Any]:
        """Agrupa equipamentos por código mostrando totais de Novo e Usado"""
        # Converter código para string se necessário
        if isinstance(codigo, str):
            codigo_para_busca = codigo.upper()
        else:
            codigo_para_busca = str(codigo)

        equipamentos = self.obter_equipamento_por_codigo(codigo_para_busca)
        
        if not equipamentos:
            return {}
        
        resultado = {
            'codigo_produto': codigo_para_busca,
            'equipamento': equipamentos[0]['equipamento'],
            'categoria': equipamentos[0]['categoria'],
            'marca': equipamentos[0]['marca'],
            'modelo': equipamentos[0]['modelo'],
            'qtd_novos': 0,
            'qtd_usados': 0,
            'valor_novos': 0.0,
            'valor_usados': 0.0,
            'fornecedor': equipamentos[0]['fornecedor']
        }
        
        for eq in equipamentos:
            condicao_raw = eq.get('condicao', 'N/A')
            quantidade = eq.get('quantidade', 0)
            valor = eq.get('valor_unitario', 0.0)

            # Normalizar condição para comparação correta
            condicao_normalizada = self._normalizar_condicao(condicao_raw)

            if condicao_normalizada == CondicionEquipamento.NOVO.value:
                resultado['qtd_novos'] = quantidade
                resultado['valor_novos'] = valor
            elif condicao_normalizada == CondicionEquipamento.USADO.value:
                resultado['qtd_usados'] = quantidade
                resultado['valor_usados'] = valor
        
        resultado['qtd_total'] = resultado['qtd_novos'] + resultado['qtd_usados']
        resultado['valor_medio'] = (
            (resultado['qtd_novos'] * resultado['valor_novos'] + 
             resultado['qtd_usados'] * resultado['valor_usados']) / 
            resultado['qtd_total'] if resultado['qtd_total'] > 0 else 0
        )
        
        return resultado

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

    def codigo_existe(self, codigo, excluir_id: Optional[int] = None) -> bool:
        """Verifica se código já existe (qualquer condição)"""
        # Converter código para o mesmo tipo da coluna para comparação correta
        if isinstance(codigo, str):
            try:
                if self.df_estoque['codigo_produto'].dtype == 'int64':
                    codigo_comparacao = int(codigo)
                else:
                    codigo_comparacao = codigo.upper()
            except ValueError:
                codigo_comparacao = codigo.upper()
        else:
            codigo_comparacao = codigo

        df_filtrado = self.df_estoque[self.df_estoque['codigo_produto'] == codigo_comparacao]
        if excluir_id:
            df_filtrado = df_filtrado[df_filtrado['id'] != excluir_id]
        return not df_filtrado.empty
    
    def codigo_e_condicao_existe(self, codigo, condicao: CondicionEquipamento, excluir_id: Optional[int] = None) -> bool:
        """Verifica se código com condição específica já existe"""
        # Converter código para o mesmo tipo da coluna para comparação correta
        if isinstance(codigo, str):
            try:
                if self.df_estoque['codigo_produto'].dtype == 'int64':
                    codigo_comparacao = int(codigo)
                else:
                    codigo_comparacao = codigo.upper()
            except ValueError:
                codigo_comparacao = codigo.upper()
        else:
            codigo_comparacao = codigo

        # Filtrar por código primeiro
        df_filtrado = self.df_estoque[self.df_estoque['codigo_produto'] == codigo_comparacao]

        # Aplicar filtro de condição com normalização
        equipamentos_filtrados = []
        for idx, row in df_filtrado.iterrows():
            if excluir_id and row['id'] == excluir_id:
                continue
            condicao_normalizada = self._normalizar_condicao(row['condicao'])
            if condicao_normalizada == condicao.value:
                equipamentos_filtrados.append(row)

        return len(equipamentos_filtrados) > 0
    
    def listar_codigos_duplicados(self) -> List[str]:
        """Lista códigos que aparecem em múltiplos produtos (ignora condição)"""
        if self.df_estoque.empty:
            return []
        
        # Agrupar por código e contar produtos únicos (nome + marca + modelo)
        df_produtos = self.df_estoque.groupby('codigo_produto').agg({
            'equipamento': 'nunique',
            'marca': 'nunique', 
            'modelo': 'nunique'
        }).reset_index()
        
        # Códigos onde qualquer campo tem mais de 1 valor único = produtos diferentes
        codigos_duplicados = df_produtos[
            (df_produtos['equipamento'] > 1) | 
            (df_produtos['marca'] > 1) | 
            (df_produtos['modelo'] > 1)
        ]['codigo_produto'].tolist()
        
        return codigos_duplicados
    
    def remover_equipamento_por_id(self, equipamento_id: int) -> EquipamentoResponse:
        """Remove equipamento pelo ID"""
        try:
            if equipamento_id not in self.df_estoque['id'].values:
                return EquipamentoResponse(
                    success=False,
                    message=f"Equipamento com ID {equipamento_id} não encontrado"
                )
            
            # Obter informações do equipamento antes de remover
            equipamento_info = self.df_estoque[self.df_estoque['id'] == equipamento_id].iloc[0]
            
            # Remover do DataFrame
            self.df_estoque = self.df_estoque[self.df_estoque['id'] != equipamento_id]
            
            # Salvar dados
            self.excel_service.salvar_dados(self.df_estoque, self.df_movimentacoes)
            
            logger.info(f"✅ Equipamento removido: ID {equipamento_id} - {equipamento_info['equipamento']}")
            
            return EquipamentoResponse(
                success=True,
                message=f"Equipamento '{equipamento_info['equipamento']}' removido com sucesso"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover equipamento ID {equipamento_id}: {str(e)}")
            return EquipamentoResponse(
                success=False,
                message=f"Erro ao remover equipamento: {str(e)}"
            )
    
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
            
            # Verificar unicidade do código baseado na configuração
            if settings.CODIGO_UNICO_OBRIGATORIO:
                # Modo: Código deve ser único (mesmo produto em diferentes condições)
                if self.codigo_existe(equipamento_sanitized.codigo_produto):
                    logger.warning(f"🚨 Tentativa de adicionar código duplicado: {equipamento_sanitized.codigo_produto}")
                    return EquipamentoResponse(
                        success=False,
                        message=f"Código '{equipamento_sanitized.codigo_produto}' já existe. Use códigos únicos para cada produto."
                    )
            else:
                # Modo: Código + condição deve ser único (produtos diferentes podem ter mesmo código)
                if self.codigo_e_condicao_existe(equipamento_sanitized.codigo_produto, equipamento_sanitized.condicao):
                    logger.warning(f"🚨 Tentativa de adicionar código+condição duplicado: {equipamento_sanitized.codigo_produto} ({equipamento_sanitized.condicao.value})")
                    return EquipamentoResponse(
                        success=False,
                        message=f"Código '{equipamento_sanitized.codigo_produto}' com condição '{equipamento_sanitized.condicao.value}' já existe"
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
                observacoes=f"Adição inicial ao estoque | Código: {equipamento_sanitized.codigo_produto} | Condição: {equipamento_sanitized.condicao.value}",
                codigo_produto=str(equipamento_sanitized.codigo_produto),
                condicao=equipamento_sanitized.condicao
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
    
    def aumentar_estoque(self, equipamento_id: int, quantidade: int, valor_unitario: float, fornecedor: str, condicao: Optional[CondicionEquipamento] = None) -> EquipamentoResponse:
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
            
            # Usar condição do equipamento se não especificada, com tratamento seguro
            if condicao:
                condicao_final = condicao
            else:
                # Converter string para enum de forma segura
                condicao_str = equipamento.get('condicao', CondicionEquipamento.NOVO.value)
                if condicao_str == CondicionEquipamento.NOVO.value:
                    condicao_final = CondicionEquipamento.NOVO
                elif condicao_str == CondicionEquipamento.USADO.value:
                    condicao_final = CondicionEquipamento.USADO
                else:
                    # Fallback para NOVO se valor inválido
                    logger.warning(f"Condição inválida encontrada: {condicao_str}. Usando NOVO como fallback.")
                    condicao_final = CondicionEquipamento.NOVO
            
            # Registrar movimentação
            movimentacao = Movimentacao(
                equipamento_id=equipamento_id,
                tipo_movimentacao=TipoMovimentacao.ENTRADA,
                quantidade=quantidade,
                destino_origem=f"Fornecedor: {fornecedor}",
                observacoes=f"Aumento de estoque | Código: {equipamento['codigo_produto']} | Condição: {condicao_final.value}",
                codigo_produto=str(equipamento['codigo_produto']),
                condicao=condicao_final
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
    
    def remover_equipamento(self, equipamento_id: int, quantidade: int, destino: str, observacoes: str = "", condicao: Optional[CondicionEquipamento] = None) -> EquipamentoResponse:
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
            
            # Usar condição do equipamento se não especificada, com tratamento seguro
            if condicao:
                condicao_final = condicao
            else:
                # Converter string para enum de forma segura
                condicao_str = equipamento.get('condicao', CondicionEquipamento.NOVO.value)
                if condicao_str == CondicionEquipamento.NOVO.value:
                    condicao_final = CondicionEquipamento.NOVO
                elif condicao_str == CondicionEquipamento.USADO.value:
                    condicao_final = CondicionEquipamento.USADO
                else:
                    # Fallback para NOVO se valor inválido
                    logger.warning(f"Condição inválida encontrada: {condicao_str}. Usando NOVO como fallback.")
                    condicao_final = CondicionEquipamento.NOVO
            
            # Registrar movimentação
            observacoes_completas = f"{observacoes} | Código: {equipamento['codigo_produto']} | Condição: {condicao_final.value}" if observacoes else f"Código: {equipamento['codigo_produto']} | Condição: {condicao_final.value}"
            
            movimentacao = Movimentacao(
                equipamento_id=equipamento_id,
                tipo_movimentacao=TipoMovimentacao.SAIDA,
                quantidade=quantidade,
                destino_origem=destino,
                observacoes=observacoes_completas,
                codigo_produto=str(equipamento['codigo_produto']),
                condicao=condicao_final
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
    
    def calcular_rotatividade(self, dias: int = 30) -> float:
        """
        Calcula taxa de rotatividade do estoque nos últimos N dias
        
        Args:
            dias: Número de dias para análise (padrão: 30)
        
        Returns:
            Taxa de rotatividade em percentual
        
        Fórmula: (Total de saídas / Estoque médio) * 100
        """
        try:
            from datetime import datetime, timedelta
            
            # Data de corte
            data_corte = datetime.now() - timedelta(days=dias)
            
            # Filtrar movimentações recentes
            df_mov = self.df_movimentacoes.copy()
            df_mov['data_movimentacao'] = pd.to_datetime(df_mov['data_movimentacao'])
            
            df_recentes = df_mov[df_mov['data_movimentacao'] >= data_corte]
            
            # Total de saídas no período
            saidas = df_recentes[
                df_recentes['tipo_movimentacao'].astype(str).str.contains('Saída', na=False, case=False)
            ]['quantidade'].sum()
            
            # Estoque atual
            estoque_atual = self.df_estoque['quantidade'].sum()
            
            # Taxa de rotatividade
            if estoque_atual > 0:
                taxa = (saidas / estoque_atual) * 100
                return round(taxa, 2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Erro ao calcular rotatividade: {str(e)}")
            return 0.0
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do estoque com separação Novo/Usado"""
        try:
            # Se DataFrame está vazio, retornar estatísticas zeradas
            if self.df_estoque.empty:
                logger.info("DataFrame de estoque vazio - retornando estatísticas zeradas")
                return {
                    'total_equipamentos': 0,
                    'valor_total': 0.0,
                    'categorias_unicas': 0,
                    'disponiveis': 0,
                    'total_tipos': 0,
                    'em_manutencao': 0,
                    'total_novos': 0,
                    'total_usados': 0,
                    'valor_novos': 0.0,
                    'valor_usados': 0.0,
                    'percentual_novos': 0.0,
                    'percentual_usados': 0.0
                }
            
            # Verificar se coluna 'condicao' existe (compatibilidade com dados antigos)
            if 'condicao' not in self.df_estoque.columns:
                # Comportamento legacy
                total_equipamentos = self.df_estoque['quantidade'].sum()
                valor_total = (self.df_estoque['quantidade'] * self.df_estoque['valor_unitario']).sum()
                return {
                    'total_equipamentos': int(total_equipamentos),
                    'valor_total': float(valor_total),
                    'categorias_unicas': int(self.df_estoque['categoria'].nunique()),
                    'disponiveis': int(self.df_estoque[self.df_estoque['status'] == StatusEquipamento.DISPONIVEL]['quantidade'].sum()),
                    'total_tipos': len(self.df_estoque),
                    'em_manutencao': len(self.df_estoque[self.df_estoque['status'] == StatusEquipamento.MANUTENCAO]),
                    # Valores zerados para novo/usado
                    'total_novos': 0,
                    'total_usados': 0,
                    'valor_novos': 0.0,
                    'valor_usados': 0.0,
                    'percentual_novos': 0.0,
                    'percentual_usados': 0.0
                }
            
            # Estatísticas com separação Novo/Usado (usando normalização)
            df_novos = self.df_estoque[self.df_estoque['condicao'].apply(lambda x: self._normalizar_condicao(x)) == CondicionEquipamento.NOVO.value]
            df_usados = self.df_estoque[self.df_estoque['condicao'].apply(lambda x: self._normalizar_condicao(x)) == CondicionEquipamento.USADO.value]
            
            total_novos = df_novos['quantidade'].sum() if not df_novos.empty else 0
            total_usados = df_usados['quantidade'].sum() if not df_usados.empty else 0
            total_equipamentos = total_novos + total_usados
            
            valor_novos = (df_novos['quantidade'] * df_novos['valor_unitario']).sum() if not df_novos.empty else 0.0
            valor_usados = (df_usados['quantidade'] * df_usados['valor_unitario']).sum() if not df_usados.empty else 0.0
            valor_total = valor_novos + valor_usados
            
            percentual_novos = (total_novos / total_equipamentos * 100) if total_equipamentos > 0 else 0.0
            
            categorias_unicas = self.df_estoque['categoria'].nunique()
            disponiveis = self.df_estoque[self.df_estoque['status'] == StatusEquipamento.DISPONIVEL]['quantidade'].sum()
            
            return {
                'total_equipamentos': int(total_equipamentos),
                'valor_total': float(valor_total),
                'categorias_unicas': int(categorias_unicas),
                'disponiveis': int(disponiveis),
                'total_tipos': len(self.df_estoque),
                'em_manutencao': len(self.df_estoque[self.df_estoque['status'] == StatusEquipamento.MANUTENCAO]),
                # Novas estatísticas por condição
                'total_novos': int(total_novos),
                'total_usados': int(total_usados),
                'valor_novos': float(valor_novos),
                'valor_usados': float(valor_usados),
                'percentual_novos': float(percentual_novos),
                'percentual_usados': float(100.0 - percentual_novos),
                # Indicadores de performance
                'rotatividade_7d': self.calcular_rotatividade(7),
                'rotatividade_30d': self.calcular_rotatividade(30),
                'rotatividade_90d': self.calcular_rotatividade(90)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                'total_equipamentos': 0,
                'valor_total': 0.0,
                'categorias_unicas': 0,
                'disponiveis': 0,
                'total_tipos': 0,
                'em_manutencao': 0,
                'total_novos': 0,
                'total_usados': 0,
                'valor_novos': 0.0,
                'valor_usados': 0.0,
                'percentual_novos': 0.0,
                'percentual_usados': 0.0,
                'rotatividade_7d': 0.0,
                'rotatividade_30d': 0.0,
                'rotatividade_90d': 0.0
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
                (df_filtrado['codigo_produto'].astype(str).str.contains(codigo, case=False, na=False)) |
                (df_filtrado['equipamento'].astype(str).str.contains(codigo, case=False, na=False))
            ]
        
        return df_filtrado 