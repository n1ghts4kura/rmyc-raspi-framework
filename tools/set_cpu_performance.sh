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

# 1. 显示当前状态
echo "📊 当前状态："
echo "------------------------------------------------------------"
echo "调度器模式: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
echo "CPU 频率:"
for i in 0 1 2 3; do
    freq=$(cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_cur_freq)
    echo "  CPU $i: $freq Hz ($(echo "scale=1; $freq/1000" | bc) MHz)"
done
echo "温度: $(vcgencmd measure_temp)"
echo ""

# 2. 切换到性能模式
echo "🚀 正在切换到性能模式..."
if [ "$EUID" -ne 0 ]; then
    echo "❌ 错误：需要 root 权限"
    echo "请使用：sudo bash $0"
    exit 1
fi

# 切换所有 CPU 核心到性能模式
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null

# 等待系统调整
sleep 2

echo "✅ 切换完成！"
echo ""

# 3. 验证结果
echo "📊 切换后状态："
echo "------------------------------------------------------------"
current_governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
echo "调度器模式: $current_governor"

if [ "$current_governor" = "performance" ]; then
    echo "✅ 调度器已设置为性能模式"
else
    echo "❌ 警告：调度器未能切换到性能模式"
fi

echo "CPU 频率:"
all_max=true
for i in 0 1 2 3; do
    freq=$(cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_cur_freq)
    mhz=$(echo "scale=1; $freq/1000" | bc)
    echo "  CPU $i: $freq Hz ($mhz MHz)"
    
    # 检查是否达到最大频率 (1800 MHz = 1800000 Hz)
    if [ "$freq" -lt 1500000 ]; then
        all_max=false
    fi
done

if [ "$all_max" = true ]; then
    echo "✅ 所有核心已运行在高频状态"
else
    echo "⚠️  部分核心频率未达到最大值（正常，会在负载时自动提升）"
fi

echo "温度: $(vcgencmd measure_temp)"
echo ""

# 4. 提示
echo "============================================================"
echo "💡 提示："
echo "------------------------------------------------------------"
echo "✅ 性能模式已启用（本次启动有效）"
echo ""
echo "如需开机自动启用，请执行："
echo "  sudo bash tools/install_cpu_performance_service.sh"
echo ""
echo "恢复节能模式（降低功耗）："
echo "  echo ondemand | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
echo "============================================================"
