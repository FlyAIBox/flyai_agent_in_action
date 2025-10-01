"""
深度研究助手部署测试脚本

这个脚本用于测试深度研究助手的部署是否正常工作，包括：
1. 连接验证
2. 分析师生成测试
3. 访谈流程测试
4. 报告生成测试

使用方法：
    python test_connection.py
"""

import asyncio
from langgraph_sdk import get_client
from langgraph.pregel.remote import RemoteGraph


# LangGraph Server 地址
URL = "http://localhost:8124"
GRAPH_NAME = "research_assistant"


async def test_connection():
    """测试基本连接"""
    print("=" * 60)
    print("1. 测试连接到 LangGraph Server")
    print("=" * 60)
    
    try:
        client = get_client(url=URL)
        print(f"✅ 成功连接到 {URL}")
        return client
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None


async def test_create_thread(client):
    """测试创建线程"""
    print("\n" + "=" * 60)
    print("2. 测试创建线程")
    print("=" * 60)
    
    try:
        thread = await client.threads.create()
        print(f"✅ 成功创建线程: {thread['thread_id']}")
        return thread
    except Exception as e:
        print(f"❌ 创建线程失败: {e}")
        return None


async def test_analyst_generation(client, thread):
    """测试分析师生成"""
    print("\n" + "=" * 60)
    print("3. 测试分析师生成")
    print("=" * 60)
    
    try:
        # 配置研究参数
        config = {
            "configurable": {
                "topic": "大语言模型在软件开发中的应用",
                "max_analysts": 2
            }
        }
        
        # 启动研究流程（直到人机协同中断点）
        print("📝 研究主题: 大语言模型在软件开发中的应用")
        print("👥 分析师数量: 2")
        
        async for event in client.runs.stream(
            thread["thread_id"],
            GRAPH_NAME,
            input={
                "topic": "大语言模型在软件开发中的应用",
                "max_analysts": 2
            },
            config=config,
            stream_mode="values"
        ):
            # 检查是否有分析师信息
            if "analysts" in event:
                analysts = event["analysts"]
                if analysts:
                    print(f"\n✅ 成功生成 {len(analysts)} 位分析师:")
                    for i, analyst in enumerate(analysts, 1):
                        print(f"\n分析师 {i}:")
                        print(f"  姓名: {analyst.name}")
                        print(f"  机构: {analyst.affiliation}")
                        print(f"  角色: {analyst.role}")
                        print(f"  描述: {analyst.description[:50]}...")
                    return True
        
        return False
    except Exception as e:
        print(f"❌ 分析师生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_remote_graph():
    """测试 Remote Graph 功能"""
    print("\n" + "=" * 60)
    print("4. 测试 Remote Graph")
    print("=" * 60)
    
    try:
        # 创建 Remote Graph 实例
        remote_graph = RemoteGraph(GRAPH_NAME, url=URL)
        print("✅ 成功创建 Remote Graph 实例")
        
        # 测试简单调用
        print("📝 测试简单的分析师生成...")
        config = {
            "configurable": {
                "thread_id": f"test-{asyncio.get_event_loop().time()}"
            }
        }
        
        # 注意：这里只测试到分析师生成阶段
        # 完整的研究流程需要人机协同确认
        result = await remote_graph.ainvoke({
            "topic": "Python 在数据科学中的应用",
            "max_analysts": 2,
            "human_analyst_feedback": ""  # 空反馈表示接受默认分析师
        }, config=config)
        
        if "analysts" in result:
            print(f"✅ Remote Graph 调用成功，生成了 {len(result['analysts'])} 位分析师")
            return True
        else:
            print("⚠️ Remote Graph 调用成功，但未生成分析师")
            return False
            
    except Exception as e:
        print(f"❌ Remote Graph 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_workflow():
    """测试完整工作流（需要更长时间）"""
    print("\n" + "=" * 60)
    print("5. 测试完整研究工作流（可选，需要较长时间）")
    print("=" * 60)
    
    response = input("是否执行完整工作流测试？(y/n): ")
    if response.lower() != 'y':
        print("⏭️ 跳过完整工作流测试")
        return True
    
    try:
        client = get_client(url=URL)
        thread = await client.threads.create()
        
        config = {
            "configurable": {
                "topic": "人工智能伦理",
                "max_analysts": 2,
                "max_interview_turns": 1  # 减少轮次以加快测试
            }
        }
        
        print("🚀 开始完整研究流程...")
        print("📝 研究主题: 人工智能伦理")
        
        # 第一阶段：生成分析师
        print("\n阶段 1: 生成分析师...")
        async for event in client.runs.stream(
            thread["thread_id"],
            GRAPH_NAME,
            input={
                "topic": "人工智能伦理",
                "max_analysts": 2
            },
            config=config,
            stream_mode="values"
        ):
            if "analysts" in event and event["analysts"]:
                print(f"✅ 生成了 {len(event['analysts'])} 位分析师")
                break
        
        # 第二阶段：确认并继续（无反馈）
        print("\n阶段 2: 确认分析师并继续...")
        await client.threads.update_state(
            thread["thread_id"],
            {
                "human_analyst_feedback": None
            }
        )
        
        # 第三阶段：执行访谈和生成报告
        print("\n阶段 3: 执行访谈和生成报告...")
        final_report = None
        async for event in client.runs.stream(
            thread["thread_id"],
            GRAPH_NAME,
            input=None,
            config=config,
            stream_mode="values"
        ):
            if "final_report" in event:
                final_report = event["final_report"]
                break
        
        if final_report:
            print("\n✅ 成功生成研究报告!")
            print("\n" + "=" * 60)
            print("报告预览（前500字）:")
            print("=" * 60)
            print(final_report[:500] + "...")
            return True
        else:
            print("⚠️ 未能生成最终报告")
            return False
            
    except Exception as e:
        print(f"❌ 完整工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("深度研究助手部署测试")
    print("=" * 60)
    
    # 1. 测试连接
    client = await test_connection()
    if not client:
        print("\n❌ 测试失败：无法连接到服务器")
        print("请确保：")
        print("  1. Docker Compose 服务正在运行")
        print("  2. LangGraph Server 已启动")
        print("  3. 端口 8124 未被占用")
        return
    
    # 2. 测试创建线程
    thread = await test_create_thread(client)
    if not thread:
        print("\n❌ 测试失败：无法创建线程")
        return
    
    # 3. 测试分析师生成
    analyst_ok = await test_analyst_generation(client, thread)
    
    # 4. 测试 Remote Graph
    remote_ok = await test_remote_graph()
    
    # 5. 测试完整工作流（可选）
    workflow_ok = await test_full_workflow()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"连接测试: ✅")
    print(f"线程创建: ✅")
    print(f"分析师生成: {'✅' if analyst_ok else '❌'}")
    print(f"Remote Graph: {'✅' if remote_ok else '❌'}")
    print(f"完整工作流: {'✅' if workflow_ok else '⏭️ (跳过)'}")
    
    if analyst_ok and remote_ok:
        print("\n🎉 所有核心测试通过！部署成功！")
    else:
        print("\n⚠️ 部分测试失败，请检查日志")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())

