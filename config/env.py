class Env:
    API_BASE_URL = "https://api.example.com/v1"  # 示例基础地址
    TIMEOUT = 30  # 默认超时时间
    
    @classmethod
    def get_api_url(cls, path=""):
        return f"{cls.API_BASE_URL}{path}"