import os
import dashscope


def ImageChat():
    """智能问答助手函数"""
    # 初始化对话历史，包含 system 设定
    messages = [
        {'role': 'system',
         'content': '你是一名绘图经验丰富的科研工作者，尤其擅长使用echart, python绘制科研图表。你应该返回运行之后能够复现出我发送的图片的代码，做好注释方便使用（例如将示例地址替换为用户想要的图片地址）'}
    ]

    print("欢迎使用智能问答助手！\n")
    
    # 获取用户输入
    
    ImageContent = input("请输入图片路径：")
    # 如果用户直接回车，使用默认值
    if not ImageContent.strip():
        ImageContent = "input.png"  # 使用默认图片路径
    # 检查是否退出
    if ImageContent.lower() in ['quit', 'exit', '退出']:
        print("感谢使用，再见！")
    else:
        content = input("请输入你想问的问题；也可以直接 Enter 使用默认问题'阅读并理解这张图片，并帮我生成可以复现的 python,Echart 代码'")
        # 如果用户直接回车，使用默认问题
        if not content.strip():
            content = "阅读并理解这张图片，并帮我生成可以复现的 python,Echart 代码"
    
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
ImageChat()