@ChatController.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: str = Depends(AuthService.get_current_user)
):
    """
    流式请求对话接口 并且流式返回数据
    """
    target_payload = request.model_dump()
    target_payload.update({
        "user": current_user,
        "response_mode": "streaming"
    })

    async def stream_generator():
        try:
            async with backend_client.async_stream(
                method="POST",
                endpoint="/chat-messages",
                json_data=target_payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0  # 添加超时控制
            ) as response:
                # 处理非200状态码
                if response.status_code != 200:
                    error = await response.aread()
                    error_msg = json.dumps({"error": f"Backend error: {error.decode()}"})
                    yield f"data: {error_msg}\n\n".encode()
                    return

                # 流式数据传输
                try:
                    async for chunk in response.aiter_bytes():
                        # 检查连接状态
                        if response.is_closed:
                            break
                        yield chunk
                except httpx.RemoteProtocolError as e:
                    # 处理连接意外关闭
                    error_msg = json.dumps({"error": f"Connection closed: {str(e)}"})
                    yield f"data: {error_msg}\n\n".encode()
                except Exception as e:
                    error_msg = json.dumps({"error": f"Stream error: {str(e)}"})
                    yield f"data: {error_msg}\n\n".encode()

        except httpx.HTTPError as e:
            # 处理连接级错误
            error_msg = json.dumps({"error": f"Connection failed: {str(e)}"})
            yield f"data: {error_msg}\n\n".encode()

    return StreamingResponse(
        content=stream_generator(),
        media_type="text/event-stream"
    )