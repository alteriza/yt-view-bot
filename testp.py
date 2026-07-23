# test_proxy.py
import asyncio
import aiohttp

async def test_proxy(proxy_str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://httpbin.org/ip", proxy=proxy_str, timeout=10) as resp:
                print(f"✓ {proxy_str} => {await resp.text()}")
                return True
    except Exception as e:
        print(f"✗ {proxy_str} => {e}")
        return False

async def main():
    with open("proxies.txt") as f:
        proxies = [line.strip() for line in f if line.strip() and '://' in line]
    
    print(f"Testing {len(proxies)} proxies...")
    for p in proxies:
        await test_proxy(p)

if __name__ == "__main__":
    asyncio.run(main())