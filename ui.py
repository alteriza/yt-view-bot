#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import threading
import os
from typing import List, Optional

from bot.thorium_engine import ThoriumBot
from bot.logger import BotLogger
from bot.proxy_manager import ProxyManager

# ===================== Worker =====================
class BotWorker:
    def __init__(self, worker_id: int, url: str, duration: int, use_proxy: bool):
        self.worker_id = worker_id
        self.url = url
        self.duration = duration
        self.use_proxy = use_proxy
        self.bot = ThoriumBot()
        self.logger = BotLogger()
        self._stop_flag = False

    async def run(self, iteration: int, total_iterations: int) -> bool:
        self.bot._stop = False
        if self._stop_flag:
            self.bot._stop = True
            return False

        try:
            await self.bot.start()
            await self.bot.watch_video(
                url=self.url,
                duration_seconds=self.duration,
                iteration=iteration,
                total_iterations=total_iterations
            )
            await self.bot.close()
            return True
        except Exception as e:
            self.logger.error(f"Worker {self.worker_id} error: {e}")
            await self.bot.close()
            return False

    def stop(self):
        self._stop_flag = True
        self.bot._stop = True


# ===================== UI =====================
class YouTubeBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 YouTube Bot with Thorium")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Variabel
        self.running = False
        self.bot_workers: List[BotWorker] = []
        self.current_task: Optional[asyncio.Task] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.total_iterations = 0
        self.completed_iterations = 0

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input area
        input_frame = ttk.LabelFrame(main_frame, text="Konfigurasi", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        # URL
        ttk.Label(input_frame, text="URL Video:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.url_entry = ttk.Entry(input_frame, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W+tk.E, pady=2)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        # Jumlah Eksekusi, Durasi
        ttk.Label(input_frame, text="Jumlah Eksekusi:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.iter_entry = ttk.Entry(input_frame, width=10)
        self.iter_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.iter_entry.insert(0, "3")

        ttk.Label(input_frame, text="Durasi (detik):").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.dur_entry = ttk.Entry(input_frame, width=10)
        self.dur_entry.grid(row=1, column=3, sticky=tk.W, pady=2)
        self.dur_entry.insert(0, "30")

        # Jeda, Worker
        ttk.Label(input_frame, text="Jeda (detik):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.delay_entry = ttk.Entry(input_frame, width=10)
        self.delay_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.delay_entry.insert(0, "10")

        ttk.Label(input_frame, text="Worker Paralel:").grid(row=2, column=2, sticky=tk.W, pady=2)
        self.worker_entry = ttk.Entry(input_frame, width=10)
        self.worker_entry.grid(row=2, column=3, sticky=tk.W, pady=2)
        self.worker_entry.insert(0, "1")

        # Checkbox
        self.proxy_var = tk.BooleanVar(value=True)
        self.headless_var = tk.BooleanVar(value=False)

        ttk.Checkbutton(input_frame, text="Gunakan Proxy (skip jika tidak valid)",
                        variable=self.proxy_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(input_frame, text="Headless Mode",
                        variable=self.headless_var).grid(row=3, column=2, columnspan=2, sticky=tk.W, pady=5)

        # Tombol
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="▶ Start", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        # Log Output
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log Output", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # Status Bar
        self.status_var = tk.StringVar(value="Siap")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=2)

    def log_message(self, msg: str, color: str = "black"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n", color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        # Warna
        if color == "red":
            self.log_text.tag_config("red", foreground="red")
        elif color == "green":
            self.log_text.tag_config("green", foreground="green")
        elif color == "yellow":
            self.log_text.tag_config("yellow", foreground="orange")
        elif color == "cyan":
            self.log_text.tag_config("cyan", foreground="blue")

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def start_bot(self):
        if self.running:
            self.log_message("⚠️ Bot sudah berjalan!", "yellow")
            return

        url = self.url_entry.get().strip()
        if not url:
            self.log_message("❌ URL tidak boleh kosong!", "red")
            return

        try:
            total = int(self.iter_entry.get())
            duration = int(self.dur_entry.get())
            delay = int(self.delay_entry.get())
            workers = int(self.worker_entry.get())
            use_proxy = self.proxy_var.get()
            headless = self.headless_var.get()
        except ValueError:
            self.log_message("❌ Input harus angka!", "red")
            return

        if workers < 1:
            workers = 1
        if total < 1:
            total = 1

        os.environ["HEADLESS"] = str(headless).lower()

        self.running = True
        self.total_iterations = total
        self.completed_iterations = 0
        self.progress['maximum'] = total
        self.progress['value'] = 0

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.log_message(f"🚀 Memulai bot dengan {workers} worker, {total} eksekusi", "cyan")
        self.log_message(f"📺 URL: {url}, Durasi: {duration}s, Jeda: {delay}s", "cyan")
        if use_proxy:
            proxy_mgr = ProxyManager()
            proxy_count = proxy_mgr.count()
            if proxy_count > 0:
                self.log_message(f"🌐 Proxy aktif ({proxy_count} tersedia, akan skip jika tidak valid)", "green")
            else:
                self.log_message("⚠️ Tidak ada proxy, lanjut tanpa proxy", "yellow")
        else:
            self.log_message("🌐 Proxy dinonaktifkan", "yellow")

        self.status_var.set("Berjalan...")

        # Jalankan di thread terpisah
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop,
                         args=(url, total, duration, delay, workers, use_proxy),
                         daemon=True).start()

    def _run_loop(self, url, total, duration, delay, workers, use_proxy):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(
            self._run_bot(url, total, duration, delay, workers, use_proxy)
        )
        self.loop.close()

    async def _run_bot(self, url: str, total: int, duration: int,
                       delay: int, workers: int, use_proxy: bool):
        self.bot_workers = [BotWorker(i, url, duration, use_proxy) for i in range(workers)]
        sem = asyncio.Semaphore(workers)

        async def run_one(iteration: int, worker_idx: int) -> bool:
            async with sem:
                worker = self.bot_workers[worker_idx % len(self.bot_workers)]
                return await worker.run(iteration, total)

        tasks = []
        for i in range(1, total + 1):
            worker_idx = (i - 1) % workers
            tasks.append(run_one(i, worker_idx))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update UI
        def update_ui():
            for idx, result in enumerate(results, 1):
                if isinstance(result, Exception):
                    self.log_message(f"❌ Iterasi {idx} gagal: {result}", "red")
                elif result:
                    self.completed_iterations += 1
                    self.update_progress(self.completed_iterations)
                    self.log_message(f"✅ Iterasi {idx} selesai", "green")
                else:
                    self.log_message(f"⚠️ Iterasi {idx} dibatalkan", "yellow")

                if idx < total and delay > 0:
                    # Jeda dilakukan di luar, tidak perlu di sini
                    pass

            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_var.set("Selesai")
            self.log_message(f"🏁 Selesai! {self.completed_iterations}/{total} berhasil", "green")

        self.root.after(0, update_ui)

    def stop_bot(self):
        if not self.running:
            self.log_message("⚠️ Tidak ada proses berjalan", "yellow")
            return

        self.log_message("⏹ Menghentikan bot...", "yellow")
        for w in self.bot_workers:
            w.stop()
        if self.current_task:
            self.current_task.cancel()
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Dihentikan")
        self.log_message("⏹ Bot dihentikan oleh user", "yellow")

    def on_closing(self):
        if self.running:
            self.stop_bot()
        self.root.destroy()


# ===================== Main =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()