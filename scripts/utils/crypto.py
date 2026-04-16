"""
Encryption Utilities Module
加密工具模块

Handles secure credential storage and data encryption
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazdat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoManager:
    """加密管理器"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        初始化加密管理器
        
        Args:
            key: 加密密钥（自动生成如果不提供）
        """
        if key:
            self.key = key
        else:
            self.key = self._generate_key()
            
        self.fernet = Fernet(self.key)
        
    def _generate_key(self) -> bytes:
        """生成新密钥"""
        return Fernet.generate_key()
    
    @classmethod
    def derive_key_from_password(cls, password: str, 
                                  salt: Optional[bytes] = None) -> tuple:
        """
        从密码派生密钥
        
        Args:
            password: 密码
            salt: 盐值（自动生成如果不提供）
            
        Returns:
            (密钥, 盐值)元组
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt(self, data: str) -> str:
        """
        加密字符串
        
        Args:
            data: 待加密数据
            
        Returns:
            加密后的Base64字符串
        """
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """
        解密字符串
        
        Args:
            encrypted_data: 加密数据
            
        Returns:
            解密后的字符串或None
        """
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"[CryptoManager] 解密失败: {e}")
            return None
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> bool:
        """
        加密文件
        
        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            encrypted = self.fernet.encrypt(data)
            
            output_path = output_path or f"{file_path}.encrypted"
            with open(output_path, 'wb') as f:
                f.write(encrypted)
                
            return True
        except Exception as e:
            print(f"[CryptoManager] 文件加密失败: {e}")
            return False
    
    def decrypt_file(self, file_path: str, output_path: Optional[str] = None) -> bool:
        """
        解密文件
        
        Args:
            file_path: 加密文件路径
            output_path: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'rb') as f:
                encrypted = f.read()
                
            decrypted = self.fernet.decrypt(encrypted)
            
            output_path = output_path or file_path.replace('.encrypted', '')
            with open(output_path, 'wb') as f:
                f.write(decrypted)
                
            return True
        except Exception as e:
            print(f"[CryptoManager] 文件解密失败: {e}")
            return False
    
    def save_key(self, key_path: str = "./.key"):
        """
        保存密钥到文件
        
        Args:
            key_path: 密钥文件路径
        """
        with open(key_path, 'wb') as f:
            f.write(self.key)
            
    @classmethod
    def load_key(cls, key_path: str = "./.key") -> Optional[bytes]:
        """
        从文件加载密钥
        
        Args:
            key_path: 密钥文件路径
            
        Returns:
            密钥或None
        """
        try:
            with open(key_path, 'rb') as f:
                return f.read()
        except:
            return None


class SecureStorage:
    """安全存储"""
    
    def __init__(self, storage_path: str = "./.secure_data", 
                 key_path: str = "./.key"):
        """
        初始化安全存储
        
        Args:
            storage_path: 存储文件路径
            key_path: 密钥文件路径
        """
        self.storage_path = storage_path
        
        # 加载或生成密钥
        key = CryptoManager.load_key(key_path)
        if key:
            self.crypto = CryptoManager(key)
        else:
            self.crypto = CryptoManager()
            self.crypto.save_key(key_path)
            
    def store(self, key: str, value: str):
        """
        安全存储数据
        
        Args:
            key: 数据键
            value: 数据值
        """
        import json
        
        data = {}
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    encrypted_data = f.read()
                    decrypted = self.crypto.decrypt(encrypted_data)
                    if decrypted:
                        data = json.loads(decrypted)
            except:
                pass
                
        data[key] = value
        
        encrypted = self.crypto.encrypt(json.dumps(data))
        with open(self.storage_path, 'w') as f:
            f.write(encrypted)
            
    def retrieve(self, key: str) -> Optional[str]:
        """
        检索安全存储的数据
        
        Args:
            key: 数据键
            
        Returns:
            数据值或None
        """
        import json
        
        if not os.path.exists(self.storage_path):
            return None
            
        try:
            with open(self.storage_path, 'r') as f:
                encrypted_data = f.read()
                
            decrypted = self.crypto.decrypt(encrypted_data)
            if not decrypted:
                return None
                
            data = json.loads(decrypted)
            return data.get(key)
            
        except Exception as e:
            print(f"[SecureStorage] 检索失败: {e}")
            return None
            
    def delete(self, key: str) -> bool:
        """
        删除存储的数据
        
        Args:
            key: 数据键
            
        Returns:
            是否成功
        """
        import json
        
        if not os.path.exists(self.storage_path):
            return False
            
        try:
            with open(self.storage_path, 'r') as f:
                encrypted_data = f.read()
                
            decrypted = self.crypto.decrypt(encrypted_data)
            if not decrypted:
                return False
                
            data = json.loads(decrypted)
            
            if key in data:
                del data[key]
                encrypted = self.crypto.encrypt(json.dumps(data))
                with open(self.storage_path, 'w') as f:
                    f.write(encrypted)
                return True
            return False
            
        except:
            return False
