# bot/proxy_manager.py
import random
import aiohttp
import asyncio
from typing import Optional, List

class ProxyManager:
    def __init__(self, proxy_file="proxies.txt"):
        self.proxies = self._load_proxies(proxy_file)
        self.current_index = 0
        self.valid_proxies = []  # proxy yang sudah divalidasi (opsional)
        
    def _load_proxies(self, file) -> List[str]:
        try:
            with open(file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
                # Filter proxy dengan format benar (minimal ada://)
                return [p for p in proxies if '://' in p]
        except FileNotFoundError:
            return []
    
    def get_next(self) -> Optional[str]:
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index % len(self.proxies)]
        self.current_index += 1
        return proxy
    
    def get_random(self) -> Optional[str]:
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    async def validate(self, proxy_str: str) -> bool:
        """Cek apakah proxy bisa connect ke internet"""
        try:
            # Test akses ke httpbin.org
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy_str,
                    timeout=10
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"Proxy {proxy_str} tidak valid: {e}")
            return False
    
    def count(self) -> int:
        return len(self.proxies)
    
    async def get_valid_random(self) -> Optional[str]:
        """Ambil proxy random yang valid (timeout 10 detik per proxy)"""
        if not self.proxies:
            return None
        
        # Coba beberapa kali
        for _ in range(min(5, len(self.proxies))):
            proxy = self.get_random()
            if await self.validate(proxy):
                return proxy
        return None