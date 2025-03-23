import os
import base64
from openai import OpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
import logging

class QwenVL72bClient:
    def __init__(self):

        self.api_key = os.environ.get('OPENAI_API_KEY_QIANWEN')
        self.base_url = os.environ.get('OPENAI_API_URL_QIANWEN')
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def send_request_with_base64_image(self, base64_image, text_prompt="告诉我什么东西以及什么品牌,纯中文,信息只包含品牌和物品连在一起说"):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        try:
            responce = self.client.chat.completions.create(
                model=os.environ.get('OPENAI_API_MODEL_QIANWEN'),
                messages=messages
            )
            return responce.choices[0].message.content
        except Exception as e:
            print(f"请求发生错误: {e}")
            return None
 


class LangChainChat:
    def __init__(self, session_id: str = "default_session"):
        # 初始化模型
        self.model = ChatOpenAI(
            model=os.getenv("ALI_MODEL_PATH"),
            temperature=0.6,
            openai_api_key=os.getenv("ALI_API_KEY"),
            openai_api_base=os.getenv("ALI_API_BASE")
        )
        # 提示模板
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个乐于助人的助手。用{language}尽你所能回答所有问题。"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        self.chain = self.prompt_template | self.model
        # 使用字典存储会话历史
        self.store = {}
        # 配置会话 ID
        self.config = {'configurable': {'session_id': session_id}}

    def get_session_history(self, session_id: str) -> ChatMessageHistory:
        """获取或创建会话历史"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def init_chain_with_history(self):
        """初始化带历史记录的链"""
        return RunnableWithMessageHistory(
            self.chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def format_conversation_history(self, history):
        """将对话历史格式化为指定的 JSON 格式"""
        formatted_history = []
        for msg in history.messages:
            if isinstance(msg, HumanMessage):
                formatted_history.append({
                    "role": "user",
                    "type": "text",
                    "content": msg.content
                })
            elif isinstance(msg, AIMessage):
                formatted_history.append({
                    "role": "system",
                    "type": "text",
                    "content": msg.content
                })
        return {"conversation": formatted_history}

    def load_conversation_history(self, session_id: str, history_data: dict):
        """加载外部 JSON 格式的对话历史"""
        history = self.get_session_history(session_id)
        for msg in history_data.get("conversation", []):
            if msg["role"] == "user":
                history.add_message(HumanMessage(content=msg["content"]))
            elif msg["role"] == "system":
                history.add_message(AIMessage(content=msg["content"]))

    def run_chat(self, input_text: str, language: str = "中文", is_streaming: bool = False):
        """运行对话"""
        do_message = self.init_chain_with_history()
        session_id = self.config['configurable']['session_id']
        history = self.get_session_history(session_id)

        if is_streaming:
            # 流式对话（不打印中间结果）
            full_response = []
            for chunk in do_message.stream(
                    {"input": input_text, "language": language},
                    config=self.config
            ):
                full_response.append(chunk.content)

            response_content = "".join(full_response)
            # 删除冗余开头（从第一个"---"后开始截取）
            if "---" in response_content:
                response_content = response_content.split("---", 1)[1].strip()
            # 删除 ** 和 ###
            response_content = response_content.replace("**", "").replace("###", "")
            # 删除 --- 和上下换行符
            response_content = response_content.replace("---", "").replace("\n---\n", "")
            # 去除多余空白
            import re
            response_content = re.sub(r'\n\s*\n', '\n', response_content).strip()
            history.add_message(AIMessage(content=response_content))
            return response_content
        else:
            # 普通对话
            response = do_message.invoke(
                {"input": input_text, "language": language},
                config=self.config
            )
            response_content = response.content
            history.add_message(AIMessage(content=response_content))
            return response_content

    def get_formatted_history(self):
        """获取格式化后的对话历史"""
        session_id = self.config['configurable']['session_id']
        history = self.get_session_history(session_id)
        formatted_history = self.format_conversation_history(history)
        return formatted_history



