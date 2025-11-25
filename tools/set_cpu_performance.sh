#!/bin/bash
#
# set_cpu_performance.sh
#
# 功能：将树莓派 CPU 调度器切换到性能模式，并验证结果
# 用法：sudo bash tools/set_cpu_performance.sh
#

echo "============================================================"
echo "🔥 CPU 性能模式设置工具"
echo "============================================================"
echo ""

# 0. 基础检查
if [ ! -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
    echo "❌ 未找到 /sys/devices/system/cpu/cpu0/cpufreq"
    echo "   当前内核可能不支持 CPU 频率调节，无法设置性能模式。"
    exit 1
fi

if ! command -v bc >/dev/null 2>&1; then
    echo "⚠️ 警告：未找到 bc 命令，无法格式化显示 MHz，将继续以 Hz 显示。"
    use_bc=false
else
    use_bc=true
fi

if ! command -v vcgencmd >/dev/null 2>&1; then
    echo "⚠️ 警告：未找到 vcgencmd，无法显示温度信息。"
    have_vcgencmd=false
else
    have_vcgencmd=true
fi

# 1. 显示当前状态
echo "📊 切换前状态："
echo "------------------------------------------------------------"

if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    echo "调度器模式: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
else
    echo "调度器模式: 未找到（可能不支持 cpufreq）"
fi

echo "CPU 频率:"
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -f "$cpu/cpufreq/scaling_cur_freq" ]; then
        freq=$(cat "$cpu/cpufreq/scaling_cur_freq")
        if [ "$use_bc" = true ]; then
            mhz=$(echo "scale=1; $freq/1000" | bc)
            echo "  ${cpu##*/}: $freq Hz (${mhz} MHz)"
        else
            echo "  ${cpu##*/}: $freq Hz"
        fi
    fi
done

if [ "$have_vcgencmd" = true ]; then
    echo "温度: $(vcgencmd measure_temp)"
fi
echo ""

# 2. 切换到性能模式
echo "🚀 正在切换到性能模式..."
if [ "$EUID" -ne 0 ]; then
    echo "❌ 错误：需要 root 权限"
    echo "请使用：sudo bash $0"
    exit 1
fi

# 切换所有 CPU 核心到性能模式
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1

# 等待系统调整
sleep 2

echo "✅ 切换完成！"
echo ""

# 3. 验证结果
echo "📊 切换后状态："
echo "------------------------------------------------------------"

if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    current_governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
    echo "调度器模式: $current_governor"
    if [ "$current_governor" = "performance" ]; then
        echo "✅ 调度器已设置为性能模式"
    else
        echo "❌ 警告：调度器未能切换到性能模式"
    fi
else
    echo "调度器模式: 未找到（可能不支持 cpufreq）"
fi

echo "CPU 频率:"
all_high=true
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -f "$cpu/cpufreq/scaling_cur_freq" ]; then
        freq=$(cat "$cpu/cpufreq/scaling_cur_freq")
        if [ "$use_bc" = true ]; then
            mhz=$(echo "scale=1; $freq/1000" | bc)
            echo "  ${cpu##*/}: $freq Hz (${mhz} MHz)"
        else
            echo "  ${cpu##*/}: $freq Hz"
        fi

        # 简单判断是否“较高频率”（>= 1.5 GHz）
        if [ "$freq" -lt 1500000 ]; then
            all_high=false
        fi
    fi
done

if [ "$all_high" = true ]; then
    echo "✅ 所有核心当前频率较高，适合高负载运行"
else
    echo "⚠️ 部分核心当前频率未达到 1.5 GHz，"
    echo "   空闲时这是正常现象，负载时频率会进一步提升。"
fi

if [ "$have_vcgencmd" = true ]; then
    echo "温度: $(vcgencmd measure_temp)"
fi
echo ""

# 4. 提示
echo "============================================================"
echo "💡 提示："
echo "------------------------------------------------------------"
echo "✅ 性能模式已启用（仅在本次开机周期内有效）"
echo ""
echo "如需每次开机自动启用性能模式，请运行："
echo "  sudo bash tools/install_cpu_performance_service.sh"
echo ""
echo "如需恢复节能模式（ondemand）："
echo "  echo ondemand | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
echo "============================================================"