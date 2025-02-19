import requests
from typing import Optional, Dict, Any

class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        timeout: int = 5,
        verify_ssl: bool = True
    ):
        """
        初始化HTTP客户端
        :param base_url: 基础URL（可选）
        :param default_headers: 默认请求头（可选）
        :param timeout: 默认超时时间（秒）
        :param verify_ssl: 是否验证SSL证书
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """发送GET请求
        :param headers: 请求头（支持字典、键值对列表/集合）
        """
        """
        发送GET请求
        :param endpoint: 接口端点（相对路径）
        :param params: 查询参数
        :param headers: 请求头
        :param timeout: 超时时间（秒）
        :return: 包含响应结果的字典
        """
        return self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout
        )

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送POST请求
        :param endpoint: 接口端点（相对路径）
        :param data: 表单数据
        :param json_data: JSON数据
        :param headers: 请求头
        :param content_type: 内容类型（json/form）
        :param timeout: 超时时间（秒）
        :return: 包含响应结果的字典
        """
        return self._request(
            method="POST",
            endpoint=endpoint,
            data=data,
            json_data=json_data,
            headers=headers,
            content_type=content_type,
            timeout=timeout
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] =None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行HTTP请求
        :return: 包含状态码、响应数据和错误信息的字典
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        # 确保headers是字典类型
        headers = {**self.default_headers, **(headers or {})}
        timeout = timeout or self.timeout
        result_template = {
            "success": False,
            "status_code": None,
            "data": None,
            "error": None
        }

        try:
            # 处理不同内容类型
            if content_type == "json":
                headers.setdefault("Content-Type", "application/json")
            elif content_type == "form":
                headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            result_template["error"] = str(e)
            if e.response is not None:
                result_template["status_code"] = e.response.status_code
                try:
                    result_template["data"] = e.response.json()
                except ValueError:
                    result_template["data"] = e.response.text
            return result_template

        # 处理成功响应
        result_template["success"] = True
        result_template["status_code"] = response.status_code
        
        try:
            result_template["data"] = response.json()
        except ValueError:
            result_template["data"] = response.text

        return result_template