"""
Serviço para operações com Excel
"""

import pandas as pd
import os
from typing import Tuple, Optional
from loguru import logger
from config.settings import settings
from models.schemas import CondicionEquipamento

class ExcelService:
    """Serviço para gerenciar dados no Excel"""
    
    def __init__(self):
        self.excel_file = settings.EXCEL_FILE
        self.sheet_estoque = settings.SHEET_ESTOQUE
        self.sheet_movimentacoes = settings.SHEET_MOVIMENTACOES
    
    def carregar_dados(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Carrega dados do Excel ou cria arquivo se não existir"""
        try:
            if os.path.exists(self.excel_file):
                logger.info(f"Carregando dados do arquivo {self.excel_file}")
                
                try:
                    # Forçar codigo_produto como string ao ler
                    df_estoque = pd.read_excel(
                        self.excel_file, 
                        sheet_name=self.sheet_estoque,
                        dtype={'codigo_produto': str}
                    )
                    # Garantir que codigo_produto é string
                    if 'codigo_produto' in df_estoque.columns:
                        df_estoque['codigo_produto'] = df_estoque['codigo_produto'].astype(str)
                except Exception as e:
                    logger.warning(f"Erro ao ler sheet de estoque: {e}. Criando novo.")
                    df_estoque = pd.DataFrame()
                
                try:
                    # Forçar codigo_produto como string em movimentações também
                    df_movimentacoes = pd.read_excel(
                        self.excel_file, 
                        sheet_name=self.sheet_movimentacoes,
                        dtype={'codigo_produto': str}
                    )
                    if 'codigo_produto' in df_movimentacoes.columns:
                        df_movimentacoes['codigo_produto'] = df_movimentacoes['codigo_produto'].astype(str)
                except Exception as e:
                    logger.warning(f"Erro ao ler sheet de movimentações: {e}. Criando novo.")
                    df_movimentacoes = pd.DataFrame()
                
                # Se estoque está vazio, criar dados iniciais
                if df_estoque.empty:
                    logger.info("Sheet de estoque está vazio - criando dados iniciais")
                    return self._criar_dados_iniciais()
                
                # Migrar dados se necessário
                if 'codigo_produto' not in df_estoque.columns:
                    logger.info("Migrando dados para incluir código do produto")
                    df_estoque = self._migrar_dados(df_estoque)
                
                # Migrar para sistema Novo/Usado se necessário
                if 'condicao' not in df_estoque.columns:
                    logger.info("Migrando dados para incluir condição Novo/Usado")
                    df_estoque = self._migrar_para_novo_usado(df_estoque)
                
                # Migrar movimentações se necessário
                if not df_movimentacoes.empty and 'condicao' not in df_movimentacoes.columns:
                    logger.info("Migrando movimentações para incluir condição")
                    df_movimentacoes = self._migrar_movimentacoes_condicao(df_movimentacoes)
                
                # Salvar após migrações
                self.salvar_dados(df_estoque, df_movimentacoes)
                
                return df_estoque, df_movimentacoes
            else:
                logger.info("Criando arquivo Excel inicial com dados de exemplo")
                return self._criar_dados_iniciais()
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            return self._criar_dados_iniciais()
    
    def _migrar_dados(self, df_estoque: pd.DataFrame) -> pd.DataFrame:
        """Migra dados existentes para incluir código do produto"""
        codigos = []
        for idx, row in df_estoque.iterrows():
            categoria = row['categoria']
            marca = row['marca']
            prefixo = settings.PREFIXOS_CODIGO.get(categoria, 'OUT')
            codigo = f"{prefixo}-{marca.upper()}-{idx+1:03d}"
            codigos.append(codigo)
        
        df_estoque['codigo_produto'] = codigos
        return df_estoque
    
    def _criar_dados_iniciais(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Cria estrutura inicial do Excel VAZIA para testes manuais"""
        # Criar DataFrames vazios mas com estrutura correta das colunas
        df_estoque = pd.DataFrame({
            'id': pd.Series([], dtype='int64'),
            'equipamento': pd.Series([], dtype='object'),
            'categoria': pd.Series([], dtype='object'),
            'marca': pd.Series([], dtype='object'),
            'modelo': pd.Series([], dtype='object'),
            'codigo_produto': pd.Series([], dtype='object'),
            'quantidade': pd.Series([], dtype='int64'),
            'valor_unitario': pd.Series([], dtype='float64'),
            'data_chegada': pd.Series([], dtype='object'),
            'fornecedor': pd.Series([], dtype='object'),
            'status': pd.Series([], dtype='object'),
            'condicao': pd.Series([], dtype='object')
        })
        
        df_movimentacoes = pd.DataFrame({
            'id': pd.Series([], dtype='int64'),
            'equipamento_id': pd.Series([], dtype='int64'),
            'tipo_movimentacao': pd.Series([], dtype='object'),
            'quantidade': pd.Series([], dtype='int64'),
            'data_movimentacao': pd.Series([], dtype='object'),
            'destino_origem': pd.Series([], dtype='object'),
            'observacoes': pd.Series([], dtype='object'),
            'codigo_produto': pd.Series([], dtype='object'),
            'condicao': pd.Series([], dtype='object')
        })
        
        self.salvar_dados(df_estoque, df_movimentacoes)
        logger.info("✅ Estrutura de dados VAZIA criada para testes manuais")
        return df_estoque, df_movimentacoes
    
    def _migrar_para_novo_usado(self, df_estoque: pd.DataFrame) -> pd.DataFrame:
        """Migração inteligente para sistema Novo/Usado"""
        logger.info("🔄 Iniciando migração inteligente para sistema Novo/Usado")
        
        # Se DataFrame está vazio, retorna vazio mas com estrutura correta
        if df_estoque.empty:
            logger.warning("⚠️ DataFrame de estoque está vazio - nada para migrar")
            # Retornar DataFrame vazio mas com a coluna 'condicao'
            df_empty = df_estoque.copy()
            if 'condicao' not in df_empty.columns:
                df_empty['condicao'] = []
            return df_empty
        
        # Lista para armazenar novos registros
        novos_registros = []
        proximo_id = int(df_estoque['id'].max()) + 1 if not df_estoque.empty else 1
        
        for _, row in df_estoque.iterrows():
            codigo = row['codigo_produto']
            quantidade_total = row['quantidade']
            valor_unitario = row['valor_unitario']
            
            # Heurística para classificar como Novo ou Usado
            condicao_sugerida = self._classificar_equipamento_inteligente(row)
            
            if quantidade_total <= 1:
                # Quantidade baixa - manter como está
                nova_linha = row.copy()
                nova_linha['condicao'] = condicao_sugerida
                novos_registros.append(nova_linha)
                logger.info(f"📦 {codigo}: {quantidade_total} un. → {condicao_sugerida}")
            else:
                # Quantidade maior - dividir entre Novo e Usado
                if condicao_sugerida == CondicionEquipamento.NOVO.value:
                    # Equipamento parece novo - 70% novo, 30% usado
                    qtd_novos = max(1, int(quantidade_total * 0.7))
                    qtd_usados = quantidade_total - qtd_novos
                else:
                    # Equipamento parece usado - 30% novo, 70% usado  
                    qtd_usados = max(1, int(quantidade_total * 0.7))
                    qtd_novos = quantidade_total - qtd_usados
                
                # Criar registro para equipamentos NOVOS
                if qtd_novos > 0:
                    nova_linha_novo = row.copy()
                    nova_linha_novo['quantidade'] = qtd_novos
                    nova_linha_novo['condicao'] = CondicionEquipamento.NOVO.value
                    novos_registros.append(nova_linha_novo)
                
                # Criar registro para equipamentos USADOS
                if qtd_usados > 0:
                    nova_linha_usado = row.copy()
                    nova_linha_usado['id'] = proximo_id
                    nova_linha_usado['quantidade'] = qtd_usados
                    nova_linha_usado['valor_unitario'] = valor_unitario * 0.7  # 30% desconto para usados
                    nova_linha_usado['condicao'] = CondicionEquipamento.USADO.value
                    novos_registros.append(nova_linha_usado)
                    proximo_id += 1
                
                logger.info(f"📦 {codigo}: {quantidade_total} un. → Novos: {qtd_novos} | Usados: {qtd_usados}")
        
        # Criar novo DataFrame com os registros migrados
        if novos_registros:
            df_migrado = pd.DataFrame(novos_registros)
        else:
            # Se não há registros para migrar, retorna DataFrame vazio com estrutura
            df_migrado = df_estoque.copy()
            if 'condicao' not in df_migrado.columns:
                df_migrado['condicao'] = []
        
        logger.info(f"✅ Migração concluída: {len(df_estoque)} → {len(df_migrado)} registros")
        
        return df_migrado
    
    def _classificar_equipamento_inteligente(self, row) -> str:
        """Classifica equipamento como Novo ou Usado baseado em heurísticas"""
        equipamento = str(row['equipamento']).lower()
        categoria = str(row['categoria']).lower()
        valor_unitario = float(row['valor_unitario'])
        
        # Palavras-chave que indicam equipamento usado
        palavras_usado = ['usado', 'seminovo', 'recondicionado', 'refurbished', 'segunda mão', 'outlet']
        
        # Verificar palavras-chave
        for palavra in palavras_usado:
            if palavra in equipamento:
                return CondicionEquipamento.USADO.value
        
        # Classificar por valor (valores muito baixos = possivelmente usados)
        valores_categoria = {
            'notebook': 2000.0,
            'desktop': 1500.0,
            'monitor': 500.0,
            'impressora': 800.0,
            'servidor': 8000.0,
            'periféricos': 100.0
        }
        
        valor_referencia = valores_categoria.get(categoria, 1000.0)
        
        # Se valor é menor que 60% da referência, considera usado
        if valor_unitario < (valor_referencia * 0.6):
            return CondicionEquipamento.USADO.value
        
        # Por padrão, considera novo
        return CondicionEquipamento.NOVO.value
    
    def _migrar_movimentacoes_condicao(self, df_movimentacoes: pd.DataFrame) -> pd.DataFrame:
        """Adiciona campo condição às movimentações existentes"""
        if df_movimentacoes.empty:
            df_movimentacoes['condicao'] = []
            return df_movimentacoes
        
        # Para movimentações existentes, assumir condição "Novo" por padrão
        df_movimentacoes['condicao'] = CondicionEquipamento.NOVO.value
        
        # Atualizar observações para incluir condição
        for idx, row in df_movimentacoes.iterrows():
            obs_atual = str(row['observacoes']) if pd.notna(row['observacoes']) else ""
            if "Condição:" not in obs_atual:
                nova_obs = f"{obs_atual} | Condição: Novo (migração)" if obs_atual else "Condição: Novo (migração)"
                df_movimentacoes.loc[idx, 'observacoes'] = nova_obs
        
        logger.info(f"✅ Migração de movimentações concluída: {len(df_movimentacoes)} registros")
        return df_movimentacoes
    
    def salvar_dados(self, df_estoque: pd.DataFrame, df_movimentacoes: pd.DataFrame) -> bool:
        """Salva dados no Excel garantindo tipos corretos"""
        try:
            # Fazer cópias para não modificar originais
            df_estoque_save = df_estoque.copy()
            df_movimentacoes_save = df_movimentacoes.copy()
            
            # Garantir que codigo_produto é sempre salvo como STRING
            if 'codigo_produto' in df_estoque_save.columns:
                df_estoque_save['codigo_produto'] = df_estoque_save['codigo_produto'].astype(str)
            
            if 'codigo_produto' in df_movimentacoes_save.columns:
                df_movimentacoes_save['codigo_produto'] = df_movimentacoes_save['codigo_produto'].astype(str)
            
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                df_estoque_save.to_excel(writer, sheet_name=self.sheet_estoque, index=False)
                df_movimentacoes_save.to_excel(writer, sheet_name=self.sheet_movimentacoes, index=False)
            
            logger.info(f"Dados salvos com sucesso em {self.excel_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return False
    
    def backup_dados(self) -> Optional[str]:
        """Cria backup dos dados"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_estoque_{timestamp}.xlsx"
            
            if os.path.exists(self.excel_file):
                import shutil
                shutil.copy2(self.excel_file, backup_file)
                logger.info(f"Backup criado: {backup_file}")
                return backup_file
            return None
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return None 