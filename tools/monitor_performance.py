#!/usr/bin/env python3
"""
实时性能监控工具
监控树莓派 CPU/GPU 频率、温度、内存使用情况

使用方法：
    python tools/monitor_performance.py
"""

import subprocess
import time
import os
import sys

def clear_screen():
    """清屏"""
    os.system('clear' if os.name != 'nt' else 'cls')

def get_cpu_freq():
    """获取 CPU 频率（MHz）"""
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_clock', 'arm'], 
            capture_output=True, 
            text=True,
            timeout=1
        )
        freq = int(result.stdout.split('=')[1]) / 1000000
        return f"{freq:.0f} MHz"
    except:
        return "N/A"

def get_gpu_freq():
    """获取 GPU 频率（MHz）"""
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_clock', 'core'], 
            capture_output=True, 
            text=True,
            timeout=1
        )
        freq = int(result.stdout.split('=')[1]) / 1000000
        return f"{freq:.0f} MHz"
    except:
        return "N/A"

def get_temp():
    """获取 CPU 温度"""
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'], 
            capture_output=True, 
            text=True,
            timeout=1
        )
        temp_str = result.stdout.split('=')[1].strip()
        temp_val = float(temp_str.replace("'C", ""))
        
        # 根据温度添加警告标识
        if temp_val >= 75:
            return f"🔥 {temp_str} (过热！)"
        elif temp_val >= 65:
            return f"⚠️  {temp_str} (偏高)"
        else:
            return f"✅ {temp_str}"
    except:
        return "N/A"

def get_memory():
    """获取内存使用（MB）"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        
        total = int(lines[0].split()[1]) / 1024  # MB
        available = int(lines[2].split()[1]) / 1024
        used = total - available
        percentage = (used / total) * 100
        
        # 根据使用率添加警告标识
        if percentage >= 90:
            prefix = "🔥"
        elif percentage >= 75:
            prefix = "⚠️ "
        else:
            prefix = "✅"
        
        return f"{prefix} {used:.0f}/{total:.0f} MB ({percentage:.1f}%)"
    except:
        return "N/A"

def get_cpu_usage():
    """获取 CPU 使用率（需要 mpstat）"""
    try:
        # 读取 /proc/stat
        with open('/proc/stat', 'r') as f:
            cpu_line = f.readline()
        
        # 解析 CPU 时间
        cpu_times = [float(x) for x in cpu_line.split()[1:]]
        total = sum(cpu_times)
        idle = cpu_times[3]  # idle time
        
        # 简单估算（需要两次采样才能准确）
        usage = 100 - (idle / total * 100)
        
        if usage >= 90:
            prefix = "🔥"
        elif usage >= 75:
            prefix = "⚠️ "
        else:
            prefix = "✅"
        
        return f"{prefix} {usage:.1f}%"
    except:
        return "N/A"

def get_throttled_status():
    """获取降频/欠压状态"""
    try:
        result = subprocess.run(
            ['vcgencmd', 'get_throttled'], 
            capture_output=True, 
            text=True,
            timeout=1
        )
        throttled_hex = result.stdout.split('=')[1].strip()
        throttled_val = int(throttled_hex, 16)
        
        if throttled_val == 0:
            return "✅ 正常"
        
        # 解析状态位
        statuses = []
        if throttled_val & 0x1:
            statuses.append("欠压")
        if throttled_val & 0x2:
            statuses.append("频率限制")
        if throttled_val & 0x4:
            statuses.append("过热限制")
        if throttled_val & 0x8:
            statuses.append("软温度限制")
        
        return f"⚠️  {', '.join(statuses)} (0x{throttled_val:X})"
    except:
        return "N/A"

def get_gpu_memory():
    """获取 GPU 内存分配"""
    try:
        result = subprocess.run(
            ['vcgencmd', 'get_mem', 'gpu'], 
            capture_output=True, 
            text=True,
            timeout=1
        )
        return result.stdout.split('=')[1].strip()
    except:
        return "N/A"

def get_uptime():
    """获取系统运行时间"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    except:
        return "N/A"

def main():
    """主循环：每秒更新一次"""
    print("=" * 70)
    print("树莓派性能实时监控")
    print("按 Ctrl+C 退出")
    print("=" * 70)
    time.sleep(2)
    
    loop_count = 0
    
    try:
        while True:
            clear_screen()
            
            print("=" * 70)
            print(f"🍓 树莓派性能监控 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
            print()
            
            # CPU 信息
            print("📊 CPU 状态")
            print(f"   频率:   {get_cpu_freq()}")
            print(f"   温度:   {get_temp()}")
            print(f"   使用率: {get_cpu_usage()}")
            print()
            
            # GPU 信息
            print("🎮 GPU 状态")
            print(f"   频率:   {get_gpu_freq()}")
            print(f"   内存:   {get_gpu_memory()}")
            print()
            
            # 内存信息
            print("💾 内存状态")
            print(f"   {get_memory()}")
            print()
            
            # 系统状态
            print("⚡ 系统状态")
            print(f"   运行时间: {get_uptime()}")
            print(f"   电源状态: {get_throttled_status()}")
            print()
            
            # 性能建议
            print("💡 性能建议")
            
            # 解析温度
            temp_str = get_temp()
            if "过热" in temp_str:
                print("   🔥 温度过高！建议加装风扇或降低超频频率")
            elif "偏高" in temp_str:
                print("   ⚠️  温度偏高，注意散热")
            
            # 解析降频状态
            throttled = get_throttled_status()
            if "欠压" in throttled:
                print("   ⚡ 检测到欠压，请更换 5V/3A 官方电源适配器")
            if "过热限制" in throttled or "频率限制" in throttled:
                print("   🌡️  系统正在降频保护，检查散热情况")
            
            # 解析内存
            mem_str = get_memory()
            if "🔥" in mem_str:
                print("   💾 内存使用率过高，考虑关闭不必要的进程")
            
            if "✅" in temp_str and "✅" in get_throttled_status() and "✅" in mem_str:
                print("   ✨ 系统状态良好，性能最佳")
            
            print()
            print("=" * 70)
            print(f"刷新: 第 {loop_count + 1} 次 | 间隔: 1 秒 | 按 Ctrl+C 退出")
            print("=" * 70)
            
            loop_count += 1
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
        print()

if __name__ == "__main__":
    # 检查是否在树莓派上运行
    try:
        subprocess.run(['vcgencmd', 'version'], 
                      capture_output=True, 
                      check=True,
                      timeout=1)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  警告：此脚本需要在树莓派上运行")
        print("   Windows/其他平台无法获取 vcgencmd 数据")
        print()
        
        if os.name == 'nt':  # Windows
            print("💡 当前在 Windows 环境，仅用于开发")
            print("   部署到树莓派后再运行此监控工具")
            sys.exit(0)
    
    main()
