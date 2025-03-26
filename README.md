# AI CLI Tool

AI CLI Tool是一个智能命令行助手，使用DeepSeek AI API为您的日常命令行任务提供智能化建议。只需用自然语言描述您想要完成的任务，AI就会推荐最合适的命令。

## 功能特点

- 🤖 使用AI技术生成命令行建议
- 💬 支持自然语言查询
- 🔄 交互式命令选择和执行
- 🎨 彩色输出优化视觉体验
- 📝 命令历史记录
- ⚙️ 可自定义配置

## 安装

### 依赖条件

- Python 3.6+
- DeepSeek API密钥

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Smera1d0/AI-Cli-Tool.git
cd AI-Cli-Tool

# 安装
pip install .

# 或直接从当前目录安装
pip install -e .
```

## 配置

首次使用前，您需要配置DeepSeek API密钥。有两种方式：

### 1. 使用环境变量

```bash
export DEEPSEEK_API_KEY="您的DeepSeek API密钥"
```

### 2. 使用配置命令

```bash
ai --setup
```

配置文件保存在 `~/.ai_cli_config.json`。

## 使用方法

### 基本使用

```bash
# 直接查询
ai "查找大文件"

# 查询包含空格的任务
ai "压缩当前目录中的所有图片文件"
```

### 交互模式

直接运行`ai`命令不带任何参数，进入交互模式：

```bash
ai
```

在交互模式中：
- 输入自然语言描述您想完成的任务
- 从AI提供的建议中选择合适的命令
- 输入 `/bye` 退出程序

### 命令选项

```
--setup      配置AI命令行工具的API密钥和其他设置
--help       显示帮助信息并退出
```

## 示例

```bash
# 查找当前目录下的大文件
ai "查找当前目录下超过100MB的文件"

# 批量重命名文件
ai "将所有png文件重命名为jpg格式"

# 查找并删除日志文件
ai "查找并删除所有超过7天的日志文件"
```

## 提示

- 安装 `colorama` 以获得更好的彩色输出体验: `pip install colorama`
- 命令历史保存在 `~/.ai_cli_history`
- 具体描述您的需求可以获得更精确的命令建议

## 贡献

欢迎提交问题和功能请求！如果您想为项目做出贡献，请：

1. Fork项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

[MIT](LICENSE)
