#!/usr/bin/env python3
import asyncio
import sys
import os
import random
from dotenv import load_dotenv

# Import langsung dari file spesifik (lebih aman)
from bot.thorium_engine import ThoriumBot
from bot.logger import BotLogger

load_dotenv()

async def run_bot():
    logger = BotLogger()
    bot = ThoriumBot()
    
    # ===== KONFIGURASI =====
    # Ganti dengan URL dan durasi sesuai keinginan
    VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # contoh
    DURATION = 30  # detik
    TOTAL_RUNS = 3  # jumlah eksekusi (ganti proxy otomatis tiap run)
    # ========================
    
    logger.info(f"🎬 Memulai YouTube Bot dengan Thorium")
    logger.info(f"📋 Total eksekusi: {TOTAL_RUNS}, Durasi: {DURATION}s")
    
    for i in range(1, TOTAL_RUNS + 1):
        logger.info(f"\n🔄 Iterasi {i}/{TOTAL_RUNS}")
        try:
            # Start browser (proxy otomatis berganti)
            await bot.start()
            
            # Nonton video
            await bot.watch_video(
                url=VIDEO_URL,
                duration_seconds=DURATION,
                iteration=i,
                total_iterations=TOTAL_RUNS
            )
            
            # Tutup browser biar proxy berganti di iterasi berikutnya
            await bot.close()
            
            # Delay antar iterasi (biar natural)
            if i < TOTAL_RUNS:
                delay = random.randint(5, 15)
                logger.info(f"⏳ Menunggu {delay}s sebelum iterasi berikutnya...")
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.error(f"Error di iterasi {i}: {e}")
            await bot.close()
            # Lanjut ke iterasi berikutnya
            continue
    
    logger.success("🏁 Semua eksekusi selesai!")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n⚠️ Bot dihentikan oleh user")
        sys.exit(0)