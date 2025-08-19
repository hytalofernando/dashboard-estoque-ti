"""
Utilitários de segurança para sanitização e validação
"""

import html
import re
import bcrypt
import secrets
from typing import Dict, Any, Optional, Union
from loguru import logger
from datetime import datetime, timedelta
from collections import defaultdict
import streamlit as st

class InputSanitizer:
    """Classe para sanitização de inputs do usuário"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 100, allow_special: bool = False) -> str:
        """
        Sanitiza string removendo HTML e caracteres perigosos
        
        Args:
            value: String a ser sanitizada
            max_length: Tamanho máximo permitido
            allow_special: Se deve permitir caracteres especiais seguros
        
        Returns:
            String sanitizada
        """
        if not value:
            return ""
        
        # Remove espaços extras
        clean = str(value).strip()
        
        # Escapa HTML
        clean = html.escape(clean)
        
        # Remove caracteres perigosos
        if not allow_special:
            # Remove caracteres que podem ser usados para ataques
            dangerous_chars = r'[<>\"\'%;()&+\[\]{}\\|`~]'
            clean = re.sub(dangerous_chars, '', clean)
        else:
            # Remove apenas os mais perigosos
            dangerous_chars = r'[<>\"\'%;\\|`]'
            clean = re.sub(dangerous_chars, '', clean)
        
        # Remove múltiplos espaços
        clean = re.sub(r'\s+', ' ', clean)
        
        # Limita tamanho
        clean = clean[:max_length]
        
        return clean.strip()
    
    @staticmethod
    def sanitize_numeric(value: Union[str, int, float], min_val: float = 0, max_val: float = float('inf')) -> float:
        """
        Sanitiza valores numéricos
        
        Args:
            value: Valor a ser sanitizado
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
        
        Returns:
            Valor numérico sanitizado
        """
        try:
            # Converte para string e remove caracteres não numéricos (exceto . e ,)
            clean_str = re.sub(r'[^\d.,\-]', '', str(value))
            
            # Substitui vírgula por ponto (padrão brasileiro)
            clean_str = clean_str.replace(',', '.')
            
            # Remove múltiplos pontos
            parts = clean_str.split('.')
            if len(parts) > 2:
                clean_str = parts[0] + '.' + ''.join(parts[1:])
            
            # Converte para float
            numeric_value = float(clean_str) if clean_str else 0.0
            
            # Aplica limites
            numeric_value = max(min_val, min(max_val, numeric_value))
            
            return numeric_value
            
        except (ValueError, TypeError):
            logger.warning(f"Erro ao sanitizar valor numérico: {value}")
            return min_val
    
    @staticmethod
    def sanitize_code(value: str, max_length: int = 20) -> str:
        """
        Sanitiza códigos de produto (permite apenas alfanuméricos, - e _)
        
        Args:
            value: Código a ser sanitizado
            max_length: Tamanho máximo
        
        Returns:
            Código sanitizado
        """
        if not value:
            return ""
        
        # Remove espaços e converte para maiúscula
        clean = str(value).strip().upper()
        
        # Permite apenas letras, números, hífen e underscore
        clean = re.sub(r'[^A-Z0-9\-_]', '', clean)
        
        # Limita tamanho
        clean = clean[:max_length]
        
        return clean

class PasswordManager:
    """Gerenciador seguro de senhas com bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash seguro da senha usando bcrypt
        
        Args:
            password: Senha em texto plano
        
        Returns:
            Hash da senha
        """
        try:
            # Gera salt aleatório
            salt = bcrypt.gensalt(rounds=12)  # 12 rounds é um bom equilíbrio
            
            # Gera hash
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            return password_hash.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Erro ao gerar hash da senha: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
        
        Returns:
            True se a senha estiver correta
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {str(e)}")
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Gera token seguro para sessões
        
        Args:
            length: Tamanho do token
        
        Returns:
            Token hexadecimal seguro
        """
        return secrets.token_hex(length)

class RateLimiter:
    """Sistema de rate limiting para prevenir ataques"""
    
    def __init__(self, max_requests: int = 30, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.requests = defaultdict(list)
        self.blocked_ips = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica se o request é permitido
        
        Args:
            identifier: Identificador único (IP, user_id, etc.)
        
        Returns:
            True se permitido, False se bloqueado
        """
        now = datetime.now()
        
        # Verifica se está bloqueado
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                return False
            else:
                # Remove do bloqueio se expirou
                del self.blocked_ips[identifier]
        
        # Remove requests antigos
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > cutoff
        ]
        
        # Verifica se excedeu o limite
        if len(self.requests[identifier]) >= self.max_requests:
            # Bloqueia por 5 minutos
            self.blocked_ips[identifier] = now + timedelta(minutes=5)
            logger.warning(f"Rate limit excedido para {identifier}. Bloqueado por 5 minutos.")
            return False
        
        # Adiciona request atual
        self.requests[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Retorna número de requests restantes
        
        Args:
            identifier: Identificador único
        
        Returns:
            Número de requests restantes
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        current_requests = [
            req_time for req_time in self.requests[identifier] 
            if req_time > cutoff
        ]
        
        return max(0, self.max_requests - len(current_requests))

class SecurityValidator:
    """Validador de segurança para dados de entrada"""
    
    @staticmethod
    def validate_equipment_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e sanitiza dados de equipamento
        
        Args:
            data: Dados do equipamento
        
        Returns:
            Dados sanitizados
        """
        sanitizer = InputSanitizer()
        
        validated = {}
        
        # Campos de texto
        text_fields = ['equipamento', 'categoria', 'marca', 'modelo', 'fornecedor']
        for field in text_fields:
            if field in data:
                validated[field] = sanitizer.sanitize_string(
                    data[field], 
                    max_length=100,
                    allow_special=False
                )
        
        # Código do produto
        if 'codigo_produto' in data:
            validated['codigo_produto'] = sanitizer.sanitize_code(data['codigo_produto'])
        
        # Valores numéricos
        if 'quantidade' in data:
            validated['quantidade'] = int(sanitizer.sanitize_numeric(
                data['quantidade'], 
                min_val=1, 
                max_val=10000
            ))
        
        if 'valor_unitario' in data:
            validated['valor_unitario'] = sanitizer.sanitize_numeric(
                data['valor_unitario'], 
                min_val=0.01, 
                max_val=1000000
            )
        
        # Observações (permite mais caracteres especiais)
        if 'observacoes' in data:
            validated['observacoes'] = sanitizer.sanitize_string(
                data['observacoes'], 
                max_length=500,
                allow_special=True
            )
        
        return validated
    
    @staticmethod
    def validate_user_input(field_name: str, value: Any, field_type: str = "text") -> Any:
        """
        Valida input do usuário baseado no tipo do campo
        
        Args:
            field_name: Nome do campo
            value: Valor a ser validado
            field_type: Tipo do campo (text, number, code, email)
        
        Returns:
            Valor validado
        """
        sanitizer = InputSanitizer()
        
        if field_type == "text":
            return sanitizer.sanitize_string(value)
        elif field_type == "number":
            return sanitizer.sanitize_numeric(value)
        elif field_type == "code":
            return sanitizer.sanitize_code(value)
        elif field_type == "email":
            # Validação básica de email
            email = sanitizer.sanitize_string(value, allow_special=True)
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return email.lower()
            return ""
        else:
            return sanitizer.sanitize_string(value)

# Instâncias globais
rate_limiter = RateLimiter()
security_validator = SecurityValidator()
