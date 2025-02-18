from fastapi import FastAPI
from modules.controller.conversation_controller import ConversationController

app=FastAPI(title="百晓生api文档",
            description="百晓生api文档",
            version='1.0.0');



#路由列表
controller_list = [
    {'router': ConversationController, 'tags': ['会话模块']},
]

for controller in controller_list:
    app.include_router(router=controller.get('router'), tags=controller.get('tags'))


@app.get("/")
async def root():
    return{"message":"hello"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', 
                host="0.0.0.0",
                port=8001,
                reload=True
                )