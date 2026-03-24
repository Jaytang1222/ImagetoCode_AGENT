"""
交互式示例（TextChat / ImageChat）。
完整多智能体流水线（Agent1–4 + 验证器）见：main.py、agent_pipeline.py、agent1_code_generation.py 等。
"""
import os
import dashscope


def TextChat():
    """智能问答助手函数"""
    # 初始化对话历史，包含 system 设定
    messages = [
        {'role': 'system',
         'content': '你是一位经验丰富的软件工程师，现在作为我的老师教我，擅长解答编程问题，你尤其精通 python,C++,java,程序图形化和打包，各种爬虫和反爬虫。你的回答简洁高效，生成的代码尽可能贴合我原本的代码'}
    ]

    print("欢迎使用智能问答助手！输入'quit'或'exit'退出程序。\n")

    while True:
        default_value = "请介绍一下 Python 的特点"  # 设置默认值
        # 获取用户输入
        content = input("请输入你想问的问题：")
        # 如果用户直接回车，使用默认值
        if not content.strip():
            content = default_value
        # 检查是否退出
        if content.lower() in ['quit', 'exit', '退出']:
            print("感谢使用，再见！")
            break

        # 将用户问题添加到对话历史
        messages.append({'role': 'user', 'content': content})

        # 调用 API
        response = dashscope.Generation.call(
            # 若没有配置环境变量，请用百炼 API Key 将下行替换为：api_key="sk-xxx"
            api_key=os.getenv('sk-f4e0ec09df9644e4971f767054c5c43b'),
            model="qwen-plus",
            # 此处以 qwen-plus 为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=messages,
            result_format='message',
            stream=False
        )

        # 获取并打印 AI 回复
        assistant_content = response.output.choices[0].message.content

        # 将 AI 回复也添加到对话历史，保持上下文
        messages.append({'role': 'assistant', 'content': assistant_content})
        print(f"{assistant_content}")

def ImageChat():
    """智能问答助手函数"""
    # 初始化对话历史，包含 system 设定
    messages = [
        {'role': 'system',
         'content': '你是一名绘图经验丰富的科研工作者，尤其擅长使用echart, python绘制科研图表。你应该返回运行之后能够复现出我发送的图片的代码，做好注释方便使用（例如将示例地址替换为用户想要的图片地址）'}
    ]

    print("欢迎使用智能问答助手！输入'quit'或'exit'退出程序。\n")

    while True:
        # 获取用户输入

        ImageContent = input("请输入图片路径：")
        # 如果用户直接回车，使用默认值
        if not ImageContent.strip():
            ImageContent = "input.png"  # 使用默认图片路径
        # 检查是否退出
        if ImageContent.lower() in ['quit', 'exit', '退出']:
            print("感谢使用，再见！")
            break
        content = input("请输入你想问的问题；也可以直接Enter使用默认问题'阅读并理解这张图片，并帮我生成可以复现的python,Echart代码'")
        # 如果用户直接回车，使用默认问题
        if not content.strip():
            content = "阅读并理解这张图片，并帮我生成可以复现的python,Echart代码"

        # 将用户问题添加到对话历史
        messages.append({'role': 'user',
                         'content': [{'image': ImageContent},
                                     {'text': content}]
                         })

        # 调用 API - 使用多模态对话接口
        response = dashscope.MultiModalConversation.call(
            api_key=os.getenv('DASHSCOPE_API_KEY'),  # 从环境变量获取 API Key
            model='qwen3.5-plus',
            messages=messages,
            result_format='message',
            stream=False
        )

        # 获取并打印 AI 回复
        assistant_content = response.output.choices[0].message.content[0]['text']

        # 将 AI 回复也添加到对话历史，保持上下文
        messages.append({'role': 'assistant', 'content': [{'text': assistant_content}]})
        print(f"\n{assistant_content}\n")

