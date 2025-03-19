from fastapi import APIRouter, Query, HTTPException, Depends,Path,Body
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime, timedelta
from utils.http_client import HttpClient
from utils.response_util import ResponseUtil
from modules.models.chat_model import *
from config.env import SsoConfig, JwtConfig
from modules.service.auth_service import AuthService
import uuid, base64
import httpx, json
from exceptions.exception import ServiceException

from config.env import DifyConfig




backend_client = HttpClient(
    base_url=DifyConfig.dify_api_url,
    default_headers={"Authorization": f"Bearer {DifyConfig.dify_api_key}"},
)

ChatController = APIRouter(
    prefix="/chat-messages", dependencies=[Depends(AuthService.get_current_user)]
)






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



@ChatController.get("/{message_id}/suggested")
async def chat_suggest(
    message_id: str = Path(..., description="对话ID"),
    current_user:str=Depends(AuthService.get_current_user)
):
    """
    获取对话建议，根据messageID获取相应的对话建议
    """

    try:
        # 验证对话ID是否为UUID格式
            try:
                uuid_obj = uuid.UUID(message_id, version=4)
            except ValueError:
                raise ServiceException(message="消息ID格式错误")
            
            # 构造查询参数
            params = {"user": current_user}

            try:
                # 调用后端服务
                response = await backend_client.async_get(
                    endpoint=f"/messages/{message_id}/suggested",
                    params={k: v for k, v in params.items() if v is not None},
                )
            except Exception as e:
                raise ServiceException(message="服务暂时不可用，请稍后重试") from e


            if not response["success"]:
                error_data = response.get("data", {})
                error_message = error_data.get("message", "错误") if isinstance(error_data, dict) else str(error_data)[:100]

                raise ServiceException(message=f"请求后端服务失败: {error_message}")
            
                # 转换并返回标准响应格式
            return ResponseUtil.success(data=response.get("data",[]))
        
    except ServiceException as se:
        # 已知业务异常直接抛出
        raise

    except Exception as unhandled_ex:
        raise ServiceException(message="系统发生意外错误") from unhandled_ex




@ChatController.post("/{message_id}/feedbacks")
async def chat_feedbacks(
    request:ChatFeedbackRequest,
    message_id: str = Path(..., description="对话ID"),
    current_user:str=Depends(AuthService.get_current_user)
):
    """
    对对话进行点赞 点踩
    """

    try:
        # 验证对话ID是否为UUID格式
            try:
                uuid_obj = uuid.UUID(message_id, version=4)
            except ValueError:
                raise ServiceException(message="消息ID格式错误")
            
            target_payload = request.model_dump(exclude_unset=True)
            target_payload.update({
                "user": current_user,
            })
            try:
                # 调用后端服务
                response = await backend_client.async_post(
                    endpoint=f"/messages/{message_id}/feedbacks",
                    json_data=target_payload,
                    content_type="json"
                )
            except Exception as e:
                raise ServiceException(message="服务暂时不可用，请稍后重试") from e

            if not response["success"]:
                error_data = response.get("data", {})
                error_message = error_data.get("message", "错误") if isinstance(error_data, dict) else str(error_data)[:100]

                raise ServiceException(message=f"请求后端服务失败: {error_message}")
            
                # 转换并返回标准响应格式
            return ResponseUtil.success(data=response.get("data",[]))
        
    except ServiceException as se:
        # 已知业务异常直接抛出
        raise

    except Exception as unhandled_ex:
        raise ServiceException(message="系统发生意外错误") from unhandled_ex


# @ChatController.post("/chat")
# async def chat(
#     request: ChatRequest, current_user: str = Depends(AuthService.get_current_user)
# ):
#     """
#     流式请求对话接口，动态返回流式数据或JSON响应
#     """
#     target_payload = request.model_dump()
#     target_payload.update({"user": current_user, "response_mode": "streaming"})

#     try:
#         # 使用异步客户端发送流式请求
#         async with backend_client.async_stream(
#             method="POST",
#             endpoint="/chat-messages",
#             json_data=target_payload,
#             headers={"Content-Type": "application/json"}
#         ) as response:
#             # 获取响应内容类型
#             content_type = response.headers.get("Content-Type", "")
#             print(content_type)

#             # 处理JSON响应
#             if "application/json" in content_type:
#                 # 读取完整的JSON响应数据
#                 json_data = await response.aread()

#                 # 尝试解析 JSON 数据并返回错误
#                 try:
#                     json_response = json.loads(json_data)
#                     return ResponseUtil.error(msg=json_response)
#                 except json.JSONDecodeError:
#                     return ResponseUtil.error(msg="Invalid JSON received")

#             else:
#                 # 返回StreamingResponse来处理流式数据
#                 return StreamingResponse(
#                     content=stream_generator(response),
#                     media_type="text/event-stream"
#                 )

#     except httpx.HTTPError as e:
#         # 处理连接级错误
#         return ResponseUtil.error(msg=str(e))
    

#                 # 如果返回的是流式数据，返回StreamingResponse
# async def stream_generator(response):
#       try:
#           # 使用流式响应，每次获取一个chunk
#           async for chunk in response.aiter_bytes():
#               yield chunk
#       except httpx.RemoteProtocolError as e:
#           # 处理连接意外关闭
#           error_msg = json.dumps({"error": f"Connection closed: {str(e)}"})
#           yield f"data: {error_msg}\n\n".encode()
#       except Exception as e:
#           error_msg = json.dumps({"error": f"Stream error: {str(e)}"})
#           yield f"data: {error_msg}\n\n".encode()