import httpx
from typing import Optional, Dict, Any, Union, AsyncGenerator, Generator, Iterator
import json
from contextlib import contextmanager,asynccontextmanager

class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        timeout: int = 5,
        verify_ssl: bool = True,
        http2: bool = False
    ):
        """
        初始化HTTP客户端（支持同步和异步）
        :param base_url: 基础URL（可选）
        :param default_headers: 默认请求头（可选）
        :param timeout: 默认超时时间（秒）
        :param verify_ssl: 是否验证SSL证书
        :param http2: 是否启用HTTP/2
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.http2 = http2
        self._client = None
        self._async_client = None

    @property
    def client(self) -> httpx.Client:
        """同步客户端实例"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                http2=self.http2
            )
        return self._client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """异步客户端实例"""
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                http2=self.http2
            )
        return self._async_client

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        同步GET请求
        """
        return self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout
        )

    async def async_get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        异步GET请求
        """
        return await self._async_request(
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
        同步POST请求
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

    async def async_post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        异步POST请求
        """
        return await self._async_request(
            method="POST",
            endpoint=endpoint,
            data=data,
            json_data=json_data,
            headers=headers,
            content_type=content_type,
            timeout=timeout
        )



    def delete(
    self,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    content_type: str = "json",
    timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        同步DELETE请求
        """
        return self._request(
            method="DELETE",
            endpoint=endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            content_type=content_type,
            timeout=timeout
        )

    async def async_delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        异步DELETE请求
        """
        return await self._async_request(
            method="DELETE",
            endpoint=endpoint,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers,
            content_type=content_type,
            timeout=timeout
        )    

    @contextmanager
    def stream(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Iterator[httpx.Response]:
        """
        同步流式请求上下文管理器
        使用示例：
        with client.stream("GET", "/stream") as response:
            for chunk in response.iter_bytes():
                print(chunk)
        """
        headers = self._merge_headers(headers)
        self._set_content_type(headers, content_type)

        with self.client.stream(
            method=method.upper(),
            url=endpoint,
            params=params,
            data=data,
            json=json_data,
            headers=headers,
            timeout=timeout or self.timeout
        ) as response:
            yield response

    @asynccontextmanager
    async def async_stream(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> AsyncGenerator[httpx.Response, None]:
        """修复后的异步流式请求"""
        headers = self._merge_headers(headers)
        self._set_content_type(headers, content_type)

        # 确保使用正确的异步客户端
        async with self.async_client.stream(
            method=method.upper(),
            url=endpoint,
            params=params,
            data=data,
            json=json_data,
            headers=headers,
            timeout=timeout or self.timeout
        ) as response:
            yield response

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行同步HTTP请求
        """
        result_template = {
            "success": False,
            "status_code": None,
            "data": None,
            "error": None
        }

        try:
            headers = self._merge_headers(headers)
            self._set_content_type(headers, content_type)

            response = self.client.request(
                method=method.upper(),
                url=endpoint,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=timeout or self.timeout
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            return self._handle_error(e, result_template)
        except Exception as e:
            result_template["error"] = str(e)
            return result_template

        return self._handle_response(response, result_template)

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "json",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行异步HTTP请求
        """
        result_template = {
            "success": False,
            "status_code": None,
            "data": None,
            "error": None
        }

        try:
            headers = self._merge_headers(headers)
            self._set_content_type(headers, content_type)

            response = await self.async_client.request(
                method=method.upper(),
                url=endpoint,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=timeout or self.timeout
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            return self._handle_error(e, result_template)
        except Exception as e:
            result_template["error"] = str(e)
            return result_template

        return self._handle_response(response, result_template)

    def _merge_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """合并默认请求头"""
        return {**self.default_headers, **(headers or {})}

    def _set_content_type(self, headers: Dict[str, str], content_type: str):
        """设置内容类型"""
        if content_type == "json" and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        elif content_type == "form" and "Content-Type" not in headers:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

    def _handle_response(self, response: httpx.Response, result: dict) -> dict:
        """处理成功响应"""
        result["success"] = True
        result["status_code"] = response.status_code

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            result["data"] = response.json()
        else:
            result["data"] = response.text

        return result

    def _handle_error(self, error: httpx.HTTPStatusError, result: dict) -> dict:
        """处理错误响应"""
        result["error"] = str(error)
        result["status_code"] = error.response.status_code

        try:
            result["data"] = error.response.json()
        except json.JSONDecodeError:
            result["data"] = error.response.text

        return result

    def close(self):
        """关闭客户端连接"""
        if self._client:
            self._client.close()
        if self._async_client:
            self._async_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()