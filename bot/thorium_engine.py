import asyncio
import random
import os
import time
from playwright.async_api import async_playwright, Browser, Page
from dotenv import load_dotenv

from .anti_detect import get_stealth_user_agent, get_anti_fingerprint_script
from .proxy_manager import ProxyManager
from .logger import BotLogger

load_dotenv()

class ThoriumBot:
    def __init__(self):
        self.logger = BotLogger()
        self.proxy_manager = ProxyManager(os.getenv("PROXY_FILE", "proxies.txt"))
        self.browser: Browser = None
        self.page: Page = None
        self.playwright = None
        self.thorium_path = os.getenv("THORIUM_PATH", "/usr/bin/thorium-browser")
        self.headless = os.getenv("HEADLESS", "False").lower() == "true"
        self._stop = False

    async def start(self, headless=None):
        if headless is None:
            headless = self.headless

        self.playwright = await async_playwright().start()
        self.logger.info(f"🚀 Launching Thorium from: {self.thorium_path}")

        proxy_str = None
        if self.proxy_manager.count() > 0:
            valid_proxy = await self.proxy_manager.get_valid_random()
            if valid_proxy:
                proxy_str = valid_proxy
                self.logger.info(f"🌐 Using Proxy: {proxy_str}")
            else:
                self.logger.warning("⚠️ Tidak ada proxy valid, lanjut tanpa proxy")
        else:
            self.logger.info("🌐 Tidak ada proxy, lanjut tanpa proxy")

        proxy_config = {"server": proxy_str} if proxy_str else None

        args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",
            "--disable-xss-auditor",
            "--disable-accelerated-2d-canvas",
            "--disable-accelerated-video-decode",
            "--disable-http2",
            "--window-size=1920,1080",
        ]

        self.browser = await self.playwright.chromium.launch(
            executable_path=self.thorium_path,
            headless=headless,
            args=args,
            proxy=proxy_config
        )

        context = await self.browser.new_context(
            user_agent=get_stealth_user_agent(),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation", "notifications"],
            geolocation={"longitude": 41.8781, "latitude": -87.6298},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

        self.page = await context.new_page()
        await self.page.add_init_script(get_anti_fingerprint_script())

        self.logger.success("✅ Thorium browser siap dengan anti-detection aktif")
        return self.page

    async def watch_video(self, url: str, duration_seconds: int,
                          iteration: int = 1, total_iterations: int = 1):
        try:
            self.logger.info(f"📺 Navigating to: {url}")
            try:
                await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception:
                self.logger.warning("Timeout dengan domcontentloaded, coba 'commit'...")
                await self.page.goto(url, wait_until="commit", timeout=60000)

            await asyncio.sleep(random.uniform(2, 4))

            try:
                play_selectors = [
                    'button[aria-label*="play" i]',
                    'button[aria-label*="putar" i]',
                    '.ytp-play-button',
                    '[data-tooltip-target-id="ytp-play-button"]'
                ]
                for selector in play_selectors:
                    try:
                        await self.page.click(selector, timeout=2000)
                        break
                    except:
                        continue
            except:
                pass

            for _ in range(random.randint(2, 5)):
                await self.page.mouse.wheel(
                    delta_y=random.randint(100, 400),
                    delta_x=0
                )
                await asyncio.sleep(random.uniform(0.5, 2))

            self.logger.info(f"⏳ Watching for {duration_seconds} seconds...")

            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                if self._stop:
                    self.logger.warning("⏹ Dihentikan oleh user")
                    return

                elapsed = int(time.time() - start_time)
                remaining = duration_seconds - elapsed
                bar_length = 30
                filled = int((elapsed / duration_seconds) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"\r⏱ [{bar}] {elapsed}/{duration_seconds}s  (sisa: {remaining}s)", end="")
                await asyncio.sleep(1)
            print("")

            self.logger.progress_table(
                current=iteration,
                total=total_iterations,
                url=url,
                duration=duration_seconds,
                elapsed=duration_seconds
            )

            self.logger.success("✅ Video selesai ditonton!")

        except Exception as e:
            self.logger.error(f"Gagal menonton: {str(e)}")
            raise

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("🔒 Browser ditutup")