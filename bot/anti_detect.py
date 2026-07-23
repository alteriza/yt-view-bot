import random

def get_stealth_user_agent():
    """Random realistic User-Agent"""
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/128.0",
    ]
    return random.choice(ua_list)

def get_anti_fingerprint_script():
    """
    JavaScript injection via CDP (Playwright add_init_script)
    Mematikan semua sinyal WebDriver & memalsukan fingerprint
    """
    return """
    // Hilangkan property webdriver
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    
    // Manipulasi plugins
    Object.defineProperty(navigator, 'plugins', { 
        get: () => {
            const plugins = [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' }
            ];
            plugins.length = 3;
            plugins.item = (i) => plugins[i];
            return plugins;
        }
    });
    
    // Manipulasi languages
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'id-ID'] });
    
    // Chrome object
    window.chrome = { 
        runtime: {},
        loadTimes: () => {},
        csi: () => {},
        app: { isInstalled: false }
    };
    
    // Permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // Screen size umum (desktop)
    Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
    Object.defineProperty(screen, 'availHeight', { get: () => 1080 });
    Object.defineProperty(screen, 'width', { get: () => 1920 });
    Object.defineProperty(screen, 'height', { get: () => 1080 });
    
    // Hapus trace headless
    Object.defineProperty(navigator, 'headless', { get: () => false });
    
    // Fake WebGL vendor
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter(parameter);
    };
    """