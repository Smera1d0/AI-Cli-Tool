# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys
import os
import re
import argparse
import subprocess
import json
import requests
from typing import List, Dict, Optional
import readline


# Configuration
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
HISTORY_FILE = os.path.expanduser("~/.ai_cli_history")
CONFIG_FILE = os.path.expanduser("~/.ai_cli_config.json")
# print(f"Config file will be saved at: {CONFIG_FILE}")
# print(f"History file will be saved at: {HISTORY_FILE}")

# 添加彩色输出支持
try:
    from colorama import init, Fore, Style
    init()  # 初始化colorama
    COLOR_ENABLED = True
except ImportError:
    print("提示: 安装colorama以获得彩色输出 (pip install colorama)")
    COLOR_ENABLED = False
    # 如果没有colorama，创建空的颜色类
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyStyle()

class AICommandTool:
    def __init__(self):
        self.config = self.load_config()
        self.setup_history()
        
    def load_config(self) -> Dict:
        """Load configuration from config file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default config
        default_config = {
            "api_key": DEEPSEEK_API_KEY,
            "model": "deepseek-chat",
            "max_suggestions": 5
        }
        
        # Create config file if it doesn't exist
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def setup_history(self):
        """Setup command history."""
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        if os.path.exists(HISTORY_FILE):
            readline.read_history_file(HISTORY_FILE)
        
    def save_history(self):
        """Save command history."""
        readline.write_history_file(HISTORY_FILE)
    
    def get_command_suggestions(self, query: str) -> List[str]:
        """Get command suggestions from DeepSeek API."""
        if not self.config.get("api_key"):
            print("Error: DeepSeek API key not configured. Please set DEEPSEEK_API_KEY environment variable or update config file.")
            return []
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config["model"],
                    "messages": [
                        {"role": "system", "content": "You are a helpful CLI assistant. Provide practical shell commands for the user's task. Return valid shell commands only, no explanations. Do not include numbers, backticks or formatting, just return the raw commands."},
                        {"role": "user", "content": f"Suggest {self.config['max_suggestions']} shell commands for: {query}"}
                    ],
                    "max_tokens": 500
                },
                timeout=10
            )
            
            response.raise_for_status()
            suggestions = response.json()['choices'][0]['message']['content'].strip().split('\n')
            cleaned_suggestions = []
            
            for s in suggestions:
                # 清理掉可能的序号格式 (如 "1. " 或 "1- ")
                s = s.strip()
                s = re.sub(r'^\d+[\.\)-]\s*', '', s)
                # 清理掉可能的反引号
                s = s.replace('`', '')
                if s:
                    cleaned_suggestions.append(s)
                    
            return cleaned_suggestions
        
        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return []
    
    def display_suggestions(self, suggestions: List[str]) -> Optional[str]:
        """Display command suggestions and let user select one."""
        if not suggestions:
            print(f"{Fore.RED}No suggestions available.{Style.RESET_ALL}")
            return None
        
        print(f"\n{Fore.CYAN}Command suggestions:{Style.RESET_ALL}")
        for i, cmd in enumerate(suggestions, 1):
            print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {Fore.GREEN}{cmd}{Style.RESET_ALL}")
        
        try:
            choice = input(f"\n{Fore.CYAN}Select a command to execute (number), edit (e), or cancel (c): {Style.RESET_ALL}")
            
            if choice.lower() == 'c':
                return None
            elif choice.lower() == 'e':
                selected_cmd = input(f"{Fore.CYAN}Enter your custom command: {Style.RESET_ALL}")
                return selected_cmd if selected_cmd.strip() else None
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(suggestions):
                        return suggestions[idx]
                    else:
                        print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")
                        return None
                except ValueError:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                    return None
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
            return None

    def execute_command(self, command: str) -> int:
        """Execute the selected command."""
        # 确保命令不包含可能的格式问题
        command = command.replace('`', '')
        print(f"\n{Fore.CYAN}Executing: {Fore.GREEN}{command}{Style.RESET_ALL}")
        
        try:
            confirmation = input(f"{Fore.YELLOW}Proceed? (Y/n): {Style.RESET_ALL}") or "y"
            
            if confirmation.lower() != 'y':
                print(f"{Fore.YELLOW}Command execution cancelled.{Style.RESET_ALL}")
                return 0
            
            try:
                print(f"{Fore.CYAN}Output:{Style.RESET_ALL}")
                result = subprocess.run(command, shell=True)
                if result.returncode == 0:
                    print(f"\n{Fore.GREEN}Command completed successfully.{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}Command failed with exit code {result.returncode}.{Style.RESET_ALL}")
                return result.returncode
            except Exception as e:
                print(f"{Fore.RED}Error executing command: {e}{Style.RESET_ALL}")
                return 1
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Command execution cancelled.{Style.RESET_ALL}")
            return 0
    
    def run(self, query: str = None):
        """Main execution flow of the tool."""
        if not query:
            query = input(f"{Fore.CYAN}What do you want to do? {Style.RESET_ALL}")
        
        if not query.strip():
            return
        
        print(f"{Fore.YELLOW}Searching for command suggestions...{Style.RESET_ALL}")
        suggestions = self.get_command_suggestions(query)
        command = self.display_suggestions(suggestions)
        
        if command:
            self.execute_command(command)
        
        self.save_history()


def print_help():
    """打印详细的帮助信息"""
    help_text = f"""
{Fore.CYAN}====================================={Style.RESET_ALL}
{Fore.CYAN}       AI-Cli-Tool  - 帮助文档       {Style.RESET_ALL}
{Fore.CYAN}====================================={Style.RESET_ALL}

{Fore.GREEN}选项:{Style.RESET_ALL}
  {Fore.YELLOW}--setup{Style.RESET_ALL}      配置AI命令行工具的API密钥和其他设置
  {Fore.YELLOW}--help{Style.RESET_ALL}       显示此帮助信息并退出

{Fore.GREEN}示例:{Style.RESET_ALL}
  {Fore.YELLOW}ai "查找大文件"{Style.RESET_ALL}          获取查找大文件的命令建议
  {Fore.YELLOW}ai "压缩当前目录"{Style.RESET_ALL}        获取压缩当前目录的命令建议
  {Fore.YELLOW}ai --setup{Style.RESET_ALL}              配置工具API密钥和设置

{Fore.GREEN}交互模式:{Style.RESET_ALL}
  直接运行 {Fore.YELLOW}ai{Style.RESET_ALL} 无参数将进入交互模式
  在交互模式中:
  - 输入 {Fore.YELLOW}/bye{Style.RESET_ALL} 退出程序
  - 输入自然语言描述获取命令建议

{Fore.GREEN}配置:{Style.RESET_ALL}
  首次运行前，请使用 {Fore.YELLOW}--setup{Style.RESET_ALL} 配置或设置环境变量:
  {Fore.YELLOW}export DEEPSEEK_API_KEY="你的密钥"{Style.RESET_ALL}

{Fore.GREEN}提示:{Style.RESET_ALL}
  - 安装 {Fore.YELLOW}colorama{Style.RESET_ALL} 以获得彩色输出: pip install colorama
  - 命令历史保存在 {Fore.YELLOW}~/.ai_cli_history{Style.RESET_ALL}
  - 配置文件位于 {Fore.YELLOW}~/.ai_cli_config.json{Style.RESET_ALL}
    """
    print(help_text)

def main():
    parser = argparse.ArgumentParser(description="AI-powered command line tool", add_help=False)
    parser.add_argument("query", nargs="*", help="Query for command suggestions")
    parser.add_argument("--setup", action="store_true", help="Configure the AI CLI tool")
    parser.add_argument("--help", action="store_true", help="显示帮助信息")
    args = parser.parse_args()
    
    # 首先检查是否请求帮助
    if args.help or (len(sys.argv) > 1 and sys.argv[1] in ['-h', '-help']):
        print_help()
        return
    
    tool = AICommandTool()
    
    if args.setup:
        # Setup mode
        api_key = input(f"DeepSeek API Key [{tool.config.get('api_key', '')}]: ")
        model = input(f"Model name [{tool.config.get('model', 'deepseek-chat')}]: ")
        max_suggestions = input(f"Maximum suggestions [{tool.config.get('max_suggestions', 5)}]: ")
        
        if api_key:
            tool.config["api_key"] = api_key
        if model:
            tool.config["model"] = model
        if max_suggestions:
            try:
                tool.config["max_suggestions"] = int(max_suggestions)
            except ValueError:
                print("Invalid number for max suggestions. Using default.")
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(tool.config, f, indent=2)
        
        print(f"{Fore.GREEN}Configuration saved.{Style.RESET_ALL}")
        return
    
    query = " ".join(args.query)
    
    if query:  # 如果命令行提供了查询
        tool.run(query)
    else:  # 交互模式
        print(f"{Fore.CYAN}Welcome to AI Command Tool! Type {Fore.YELLOW}/bye{Fore.CYAN} to exit.{Style.RESET_ALL}")
        while True:
            try:
                query = input(f"{Fore.CYAN}What do you want to do? {Style.RESET_ALL}")
                if query.strip().lower() == '/bye':
                    print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                    break
                
                if query.strip():  # 确保查询不为空
                    print(f"{Fore.YELLOW}Searching for command suggestions...{Style.RESET_ALL}")
                    suggestions = tool.get_command_suggestions(query)
                    command = tool.display_suggestions(suggestions)
                    
                    if command:
                        tool.execute_command(command)
                    
                    tool.save_history()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)