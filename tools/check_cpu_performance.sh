#!/bin/bash
#
# check_cpu_performance.sh
#
# 功能：检查当前树莓派 CPU 性能状态，并给出优化建议
# 用法：bash tools/check_cpu_performance.sh

echo "============================================================"
echo "📊 树莓派 CPU 性能状态检查"
echo "============================================================"
echo ""

# 0. 基础环境检查
need_root=false
if ! command -v vcgencmd >/dev/null 2>&1; then
    echo "❌ 未找到 vcgencmd 命令，这通常表示："
    echo "   - 当前不是树莓派 OS，或"
    echo "   - 未安装相关工具包（libraspberrypi-bin）"
    echo ""
    echo "如为树莓派 OS，可尝试："
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y libraspberrypi-bin"
    echo ""
    exit 1
fi

if ! command -v bc >/dev/null 2>&1; then
    echo "❌ 未找到 bc 命令，用于频率计算"
    echo ""
    echo "安装方法："
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y bc"
    echo ""
    exit 1
fi

echo "✅ 基础命令检查通过 (vcgencmd / bc 可用)"
echo ""

# 1. 电源/节流状态
echo "------------------------------------------------------------"
echo "⚡ 电源与节流状态（vcgencmd get_throttled）"
echo "------------------------------------------------------------"

throttled_raw=$(vcgencmd get_throttled 2>/dev/null || echo "throttled=0x0")
echo "原始输出: $throttled_raw"

throttled_hex=${throttled_raw#*=}
# 兜底处理：如果不是以 0x 开头，直接视为 0
if [[ "$throttled_hex" != 0x* ]]; then
    throttled_hex="0x0"
fi

throttled_dec=$((16#${throttled_hex#0x}))

if [ "$throttled_dec" -eq 0 ]; then
    echo "✅ 没有检测到欠压/过热/频率限制记录"
else
    echo "⚠️ 检测到节流/电源问题："

    # 当前状态
    if (( throttled_dec & 0x1 )); then
        echo "   🔴 当前欠压！请检查电源是否稳定（建议 5V 3A）"
        need_root=true
    fi
    if (( throttled_dec & 0x2 )); then
        echo "   🔴 当前频率受限（硬件限频或电源问题）"
        need_root=true
    fi
    if (( throttled_dec & 0x4 )); then
        echo "   🔴 当前过热限流，请检查散热（风扇/散热片）"
        need_root=true
    fi

    # 历史状态
    if (( throttled_dec & 0x10000 )); then
        echo "   ⚠️ 历史记录：曾经出现欠压"
    fi
    if (( throttled_dec & 0x20000 )); then
        echo "   ⚠️ 历史记录：曾经频率受限"
    fi
    if (( throttled_dec & 0x40000 )); then
        echo "   ⚠️ 历史记录：曾经过热限流"
    fi
fi

echo ""

# 2. CPU/温度/电压
echo "------------------------------------------------------------"
echo "💻 CPU 频率 / 温度 / 电压"
echo "------------------------------------------------------------"

temp=$(vcgencmd measure_temp 2>/dev/null || echo "temp=unknown")
freq_raw=$(vcgencmd measure_clock arm 2>/dev/null || echo "frequency(48)=0")
volt=$(vcgencmd measure_volts core 2>/dev/null || echo "volt=unknown")

freq_val=${freq_raw#*=}
if [[ "$freq_val" =~ ^[0-9]+$ ]]; then
    freq_mhz=$(echo "scale=1; $freq_val/1000000" | bc)
else
    freq_mhz=0
fi

echo "温度: $temp"
echo "CPU 频率: ${freq_mhz} MHz ($freq_raw)"
echo "核心电压: $volt"
echo ""

# 3. CPU 调度器与频率范围
echo "------------------------------------------------------------"
echo "⚙️  CPU 调速器与频率范围"
echo "------------------------------------------------------------"

governor_file="/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
if [ -f "$governor_file" ]; then
    governor=$(cat "$governor_file")
    echo "当前调度器模式: $governor"
else
    echo "❌ 未找到 CPU 调度器配置文件，可能不是标准树莓派内核"
    governor="unknown"
fi

for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -e "$cpu/cpufreq/scaling_governor" ]; then
        g=$(cat "$cpu/cpufreq/scaling_governor")
        min_freq=$(cat "$cpu/cpufreq/scaling_min_freq")
        max_freq=$(cat "$cpu/cpufreq/scaling_max_freq")
        cur_freq=$(cat "$cpu/cpufreq/scaling_cur_freq")
        min_mhz=$(echo "scale=0; $min_freq/1000" | bc)
        max_mhz=$(echo "scale=0; $max_freq/1000" | bc)
        cur_mhz=$(echo "scale=1; $cur_freq/1000" | bc)
        echo "  ${cpu##*/}: $g  当前: ${cur_mhz} MHz  范围: ${min_mhz}-${max_mhz} MHz"
    fi
done

echo ""

# 4. 综合评估与建议
echo "============================================================"
echo "📝 综合评估与建议"
echo "============================================================"

# 简单规则：
# - 频率 >= 1400 MHz 且 governor=performance → 性能模式良好
# - governor=ondemand 且空闲频率低也正常（负载时会升高）
# - 若频率长期 < 1200 MHz，且需要高性能推理，建议启用性能模式

if [ "$governor" = "performance" ]; then
    if (( $(echo "$freq_mhz >= 1400" | bc) )); then
        echo "✅ 当前已是性能模式，频率较高（${freq_mhz} MHz），适合高负载推理。"
    else
        echo "⚠️ 调度器为 performance，但当前频率不高（${freq_mhz} MHz），"
        echo "   可能是空闲状态，此时属正常；在高负载时频率应提升。"
    fi
else
    echo "ℹ️ 当前调度器模式为: $governor"
    if (( $(echo "$freq_mhz >= 1400" | bc) )); then
        echo "✅ 即使不是 performance 模式，当前频率也较高（${freq_mhz} MHz）。"
    elif (( $(echo "$freq_mhz >= 1200" | bc) )); then
        echo "⚠️ 当前频率中等（${freq_mhz} MHz），用于轻度推理基本可接受。"
        echo "   若需要稳定高帧率推理，建议切换到性能模式。"
        need_root=true
    else
        echo "❌ 当前频率偏低（${freq_mhz} MHz），不利于深度学习推理性能。"
        echo "   建议切换到性能模式，并检查电源与散热。"
        need_root=true
    fi
fi

echo "============================================================"
echo "检查完成"
echo "============================================================"