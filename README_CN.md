# Namelyze

**学者国籍与性别推断工具**

[English](README.md) | 简体中文

一个研究工具，利用大语言模型（LLM）基于历史背景、文化背景和命名习惯，从学者姓名推断其国籍和性别。

## 特性

- **LLM驱动推断**：利用商业大语言模型的知识和推理能力
- **OpenAI兼容**：支持任何OpenAI兼容API（OpenAI、Azure OpenAI、DeepSeek、智谱等）
- **批量处理**：高效的批量处理以降低API成本
- **全面验证**：内置验证机制，支持错误跟踪和报告
- **置信度评级**：为每个推断提供高/中/低置信度评级
- **ISO标准**：使用ISO 3166-1 alpha-3国家代码表示国籍

## 安装

### 前置要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载此仓库

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置API设置：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API凭证
```

## 配置

编辑 `.env` 文件来配置工具：

```bash
# API配置
OPENAI_API_BASE=https://api.openai.com/v1  # 修改为你的API端点
OPENAI_API_KEY=sk-your-api-key-here        # 你的API密钥
MODEL_NAME=gpt-4                            # 要使用的模型

# 处理设置
BATCH_SIZE=20                               # 每批次处理的姓名数量
MAX_RETRIES=3                               # API调用失败重试次数
TIMEOUT=60                                  # API超时时间（秒）

# 文件路径
INPUT_CSV=data/input/names.csv              # 输入文件路径
OUTPUT_CSV=data/output/results.csv          # 输出文件路径
NAME_COLUMN=name                            # 包含姓名的列名
```

## 使用方法

### 1. 准备输入数据

创建一个包含学者姓名的CSV文件：

```csv
name
Adam Smith
Elinor Ostrom
Wei Zhang
Maria Garcia
Thomas Müller
```

将文件放在 `data/input/names.csv`（或在 `.env` 中指定的路径）

### 2. 运行工具

```bash
python main.py
```

### 3. 查看结果

结果将保存到 `data/output/results.csv`：

```csv
name,gender,conf_gender,nation,conf_nation,has_error,error_reason
Adam Smith,Male,High,GBR,High,No,
Elinor Ostrom,Female,High,USA,High,No,
Wei Zhang,Unknown,Low,CHN,High,No,
```

## 输出格式

| 列名 | 描述 |
|--------|-------------|
| `name` | 原始学者姓名（不变） |
| `gender` | 推断的性别：Male（男）、Female（女）或 Unknown（未知） |
| `conf_gender` | 性别置信度：High（高）、Medium（中）或 Low（低） |
| `nation` | ISO 3166-1 alpha-3 国家代码或 Unknown |
| `conf_nation` | 国籍置信度：High（高）、Medium（中）或 Low（低） |
| `has_error` | 是否存在验证错误：Yes 或 No |
| `error_reason` | 验证错误描述（如有） |

## 置信度级别

- **High（高）**：基于明确的历史记录、可靠的传记信息或强文化命名特征
- **Medium（中）**：基于强文化命名模式或常见国籍/性别关联，但可能存在例外
- **Low（低）**：基于模糊或跨文化通用的姓名特征，存在显著不确定性

## 支持的API提供商

本工具支持任何OpenAI兼容的API端点：

- **OpenAI官方**：`https://api.openai.com/v1`
- **Azure OpenAI**：`https://your-resource.openai.azure.com/`
- **DeepSeek**：`https://api.deepseek.com/v1`
- **智谱AI**：`https://open.bigmodel.cn/api/paas/v4/`
- **阿里云**：根据提供商文档配置
- **其他提供商**：任何支持OpenAI API格式的服务

## 错误处理

工具包含强大的错误处理机制：

- **API失败**：自动重试，使用指数退避策略
- **JSON解析错误**：捕获并在输出中报告
- **验证错误**：每个结果都会根据预期格式进行验证
- **缺失数据**：不完整的响应会标记错误原因

`error_reason` 列中的常见错误：
- `JSON parse error`：LLM响应不是有效的JSON
- `Missing in LLM response`：姓名未包含在LLM输出中
- `Invalid gender value`：性别字段包含意外值
- `Invalid nation code`：国家代码不是有效的ISO 3166-1 alpha-3代码
- `Missing [field] field`：未提供必需字段

## 项目结构

```
namelyze/
├── README.md                 # 英文文档
├── README_CN.md             # 中文文档（本文件）
├── tutorial.ipynb           # Jupyter教程
├── requirements.txt          # Python依赖
├── .env.example             # 配置模板
├── main.py                  # 主入口
├── src/
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── llm_client.py        # LLM API客户端
│   ├── prompt_template.py   # Prompt工程
│   ├── validator.py         # 结果验证
│   └── processor.py         # 核心处理逻辑
├── data/
│   ├── input/               # 输入CSV文件
│   └── output/              # 输出结果
└── examples/
    └── sample_names.csv     # 示例输入
```

## 日志

日志写入：
- **控制台**：实时进度和状态
- **文件**：`namelyze.log` 用于详细调试

## 获得最佳结果的技巧

1. **批量大小**：根据模型的上下文窗口调整 `BATCH_SIZE`
2. **模型选择**：GPT-4 通常比 GPT-3.5 提供更好的准确性
3. **成本管理**：使用批量处理最小化API调用
4. **验证**：始终审查 `has_error=Yes` 的结果以确保准确性
5. **速率限制**：如果遇到速率限制，调整 `TIMEOUT` 和 `MAX_RETRIES`

## 使用教程

我们提供了详细的Jupyter Notebook教程：

```bash
jupyter notebook tutorial.ipynb
```

教程包含：
- 环境准备
- API配置
- 数据准备
- 运行推断
- 结果分析
- 高级用法
- 常见问题

## 局限性

- **历史准确性**：结果依赖于LLM的训练数据，可能无法反映当前国籍
- **文化复杂性**：某些姓名在不同文化中确实存在歧义
- **姓名变更**：婚后姓名、音译和姓名变更可能影响准确性
- **模型依赖**：质量取决于所选LLM的能力

## 使用场景

本工具适用于以下研究场景：

- 学术研究中的作者国籍统计
- 文献计量学分析
- 科研合作网络分析
- 学科发展史研究
- 性别多样性研究

⚠️ **注意**：本工具的推断结果仅供参考，不应作为正式统计或重要决策的唯一依据。对于重要数据，建议人工复核。

## 常见问题

### Q: 为什么选择使用LLM而不是传统数据库？

A: 传统的姓名数据库方法存在以下局限：
- 商业API成本高昂
- 数据库覆盖不全面（特别是非英语姓名）
- 难以处理历史人物
- 无法利用上下文信息

LLM方法的优势：
- 具有广泛的历史和文化知识
- 能够处理各种语言和文化的姓名
- 可以提供推理依据
- 成本相对较低（批量处理）

### Q: 结果可靠吗？

A: 可靠性取决于多个因素：
- **高置信度**结果通常很可靠（基于明确的历史记录或强文化特征）
- **中置信度**结果有一定参考价值
- **低置信度**结果建议人工复核

建议：
1. 优先使用高置信度结果
2. 对低置信度结果进行人工验证
3. 可以使用多个模型交叉验证

### Q: 如何处理中文姓名？

A: 工具完全支持中文姓名。例如：
- "张伟" → CHN, Male（基于常见的中文男性姓名特征）
- "李娜" → CHN, Female（基于常见的中文女性姓名特征）

对于仅有姓氏的情况（如"王某"），性别可能返回Unknown。

### Q: 可以自定义Prompt吗？

A: 可以。编辑 `src/prompt_template.py` 文件中的 `PROMPT_TEMPLATE` 变量来自定义Prompt。

建议保持输出格式要求不变，以确保验证模块正常工作。

## 许可证

本项目按原样提供，用于研究目的。

## 贡献

欢迎贡献。请确保：
- 代码遵循现有的风格规范
- 新功能包含适当的错误处理
- 验证逻辑保持数据完整性

## 技术支持

遇到问题或有疑问：
- 查看日志文件（`namelyze.log`）获取详细错误信息
- 验证 `.env` 配置是否与 `.env.example` 匹配
- 确保API密钥和端点配置正确
- 查看输出中的 `has_error` 和 `error_reason` 列了解具体失败原因
- 参考 `tutorial.ipynb` 获取使用示例

## 更新日志

### v1.0.0 (2025-01-26)
- 初始版本发布
- 支持OpenAI兼容API
- 批量处理功能
- 完整的验证机制
- 中英文文档
- Jupyter教程

---

**开发者**: Claude Code
**项目类型**: 研究工具
**语言**: Python 3.8+
