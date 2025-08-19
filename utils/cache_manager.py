"""
Sistema de Cache Inteligente para Dashboard Estoque TI
Gerenciamento eficiente de cache com TTL e invalidação automática
"""

import time
import hashlib
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
from loguru import logger
import streamlit as st
import threading
from collections import defaultdict

class CacheManager:
    """
    Gerenciador de cache inteligente com TTL, invalidação automática e estatísticas
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutos padrão
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._access_count: Dict[str, int] = defaultdict(int)
        self._hit_count = 0
        self._miss_count = 0
        self._lock = threading.Lock()
        
        logger.info(f"🗄️ CacheManager inicializado com TTL padrão: {default_ttl}s")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Gera chave única para cache baseada nos parâmetros
        
        Args:
            prefix: Prefixo da chave
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
            
        Returns:
            Chave única para cache
        """
        # Criar string única baseada nos parâmetros
        params_str = f"{args}_{sorted(kwargs.items())}"
        hash_obj = hashlib.md5(params_str.encode())
        return f"{prefix}_{hash_obj.hexdigest()[:8]}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache se ainda válido
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor do cache ou None se expirado/inexistente
        """
        with self._lock:
            if key not in self._cache:
                self._miss_count += 1
                return None
            
            # Verificar se expirou
            if self._is_expired(key):
                self._remove(key)
                self._miss_count += 1
                return None
            
            # Cache hit
            self._hit_count += 1
            self._access_count[key] += 1
            
            return self._cache[key]['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (usa padrão se None)
        """
        with self._lock:
            ttl = ttl or self.default_ttl
            
            self._cache[key] = {
                'value': value,
                'ttl': ttl,
                'size': self._estimate_size(value)
            }
            self._timestamps[key] = datetime.now()
            
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
    
    def invalidate(self, key: str) -> bool:
        """
        Invalida entrada específica do cache
        
        Args:
            key: Chave a ser invalidada
            
        Returns:
            True se invalidada com sucesso
        """
        with self._lock:
            if key in self._cache:
                self._remove(key)
                logger.debug(f"🗑️ Cache INVALIDATED: {key}")
                return True
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida todas as entradas que correspondem ao padrão
        
        Args:
            pattern: Padrão para busca (ex: "equipamentos_*")
            
        Returns:
            Número de entradas invalidadas
        """
        with self._lock:
            keys_to_remove = []
            
            for key in self._cache.keys():
                if pattern.replace('*', '') in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._remove(key)
            
            logger.info(f"🧹 Cache pattern invalidation: {pattern} ({len(keys_to_remove)} entradas)")
            return len(keys_to_remove)
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._timestamps.clear()
            self._access_count.clear()
            
            logger.info(f"🧹 Cache completamente limpo ({count} entradas removidas)")
    
    def cleanup_expired(self) -> int:
        """
        Remove entradas expiradas do cache
        
        Returns:
            Número de entradas removidas
        """
        with self._lock:
            expired_keys = []
            
            for key in list(self._cache.keys()):
                if self._is_expired(key):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove(key)
            
            if expired_keys:
                logger.debug(f"🧹 Cache cleanup: {len(expired_keys)} entradas expiradas removidas")
            
            return len(expired_keys)
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se entrada do cache expirou"""
        if key not in self._timestamps:
            return True
        
        ttl = self._cache[key]['ttl']
        age = (datetime.now() - self._timestamps[key]).total_seconds()
        return age > ttl
    
    def _remove(self, key: str) -> None:
        """Remove entrada do cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._access_count.pop(key, None)
    
    def _estimate_size(self, value: Any) -> int:
        """Estima tamanho do valor em bytes"""
        try:
            import sys
            return sys.getsizeof(value)
        except:
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
            
            total_size = sum(entry['size'] for entry in self._cache.values())
            
            return {
                'entries': len(self._cache),
                'hit_count': self._hit_count,
                'miss_count': self._miss_count,
                'hit_rate': round(hit_rate, 2),
                'total_size_bytes': total_size,
                'most_accessed': dict(sorted(self._access_count.items(), key=lambda x: x[1], reverse=True)[:5])
            }
    
    def cache_function(self, ttl: Optional[int] = None, key_prefix: str = "func"):
        """
        Decorator para cache de funções
        
        Args:
            ttl: Tempo de vida do cache
            key_prefix: Prefixo para chave do cache
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Gerar chave única
                cache_key = self._generate_key(f"{key_prefix}_{func.__name__}", *args, **kwargs)
                
                # Tentar obter do cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"🎯 Cache HIT: {func.__name__}")
                    return cached_result
                
                # Executar função e armazenar resultado
                logger.debug(f"💾 Cache MISS: {func.__name__} - Executando função")
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            # Adicionar métodos de controle do cache à função
            wrapper.invalidate_cache = lambda *args, **kwargs: self.invalidate(
                self._generate_key(f"{key_prefix}_{func.__name__}", *args, **kwargs)
            )
            wrapper.clear_cache = lambda: self.invalidate_pattern(f"{key_prefix}_{func.__name__}")
            
            return wrapper
        return decorator

class StreamlitCacheManager(CacheManager):
    """
    Extensão do CacheManager específica para Streamlit
    Integra com session_state e fornece widgets de controle
    """
    
    def __init__(self, default_ttl: int = 300):
        super().__init__(default_ttl)
        
        # Integração com session_state
        if 'cache_manager_stats' not in st.session_state:
            st.session_state.cache_manager_stats = {}
    
    def render_cache_controls(self, show_stats: bool = True) -> None:
        """
        Renderiza controles de cache na sidebar
        
        Args:
            show_stats: Se deve mostrar estatísticas
        """
        with st.sidebar:
            st.markdown("### 🗄️ Controle de Cache")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧹 Limpar Cache", help="Remove todas as entradas do cache"):
                    self.clear()
                    st.success("Cache limpo!")
                    st.rerun()
            
            with col2:
                if st.button("🔄 Cleanup", help="Remove entradas expiradas"):
                    removed = self.cleanup_expired()
                    if removed > 0:
                        st.success(f"{removed} entradas removidas")
                    else:
                        st.info("Nenhuma entrada expirada")
            
            if show_stats:
                self._render_stats()
    
    def _render_stats(self) -> None:
        """Renderiza estatísticas do cache"""
        stats = self.get_stats()
        
        st.markdown("#### 📊 Estatísticas")
        
        # Métricas principais
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📦 Entradas", stats['entries'])
            st.metric("🎯 Taxa Hit", f"{stats['hit_rate']}%")
        
        with col2:
            st.metric("✅ Hits", stats['hit_count'])
            st.metric("❌ Misses", stats['miss_count'])
        
        # Tamanho do cache
        size_mb = stats['total_size_bytes'] / (1024 * 1024)
        st.metric("💾 Tamanho", f"{size_mb:.2f} MB")
        
        # Mais acessados
        if stats['most_accessed']:
            st.markdown("**🔥 Mais Acessados:**")
            for key, count in list(stats['most_accessed'].items())[:3]:
                st.text(f"• {key}: {count}x")
    
    def cache_dataframe(self, key: str, load_func: Callable, ttl: Optional[int] = None, 
                       force_reload: bool = False) -> Any:
        """
        Cache específico para DataFrames com opção de force reload
        
        Args:
            key: Chave do cache
            load_func: Função para carregar dados
            ttl: Tempo de vida
            force_reload: Forçar recarregamento
            
        Returns:
            DataFrame carregado
        """
        if force_reload:
            self.invalidate(key)
        
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        # Carregar dados
        data = load_func()
        self.set(key, data, ttl)
        
        return data

# Instâncias globais
cache_manager = StreamlitCacheManager()

# Decorators prontos para uso
def cache_equipment_data(ttl: int = 300):
    """Decorator para cache de dados de equipamentos"""
    return cache_manager.cache_function(ttl=ttl, key_prefix="equipment")

def cache_movement_data(ttl: int = 180):
    """Decorator para cache de dados de movimentações"""
    return cache_manager.cache_function(ttl=ttl, key_prefix="movement")

def cache_dashboard_data(ttl: int = 120):
    """Decorator para cache de dados do dashboard"""
    return cache_manager.cache_function(ttl=ttl, key_prefix="dashboard")
