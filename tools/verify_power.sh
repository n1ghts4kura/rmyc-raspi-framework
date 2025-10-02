#!/bin/bash
# 更换电源后验证脚本

echo "============================================================"
echo "⚡ 电源更换后系统验证"
echo "============================================================"

# 1. 电源状态检查
echo -e "\n📊 电源状态检查:"
throttled=$(vcgencmd get_throttled)
echo "   原始值: $throttled"

# 解析节流状态
throttled_hex=${throttled#*=}
throttled_dec=$((16#${throttled_hex#0x}))

if [ $throttled_dec -eq 0 ]; then
    echo "   ✅ 电源状态正常，无欠压/过热记录"
else
    echo "   ⚠️  检测到电源问题:"
    
    # 当前状态
    if [ $(($throttled_dec & 0x1)) -ne 0 ]; then
        echo "      🔴 当前欠压！"
    fi
    if [ $(($throttled_dec & 0x2)) -ne 0 ]; then
        echo "      🔴 当前 ARM 频率上限！"
    fi
    if [ $(($throttled_dec & 0x4)) -ne 0 ]; then
        echo "      🔴 当前过热限流！"
    fi
    
    # 历史状态
    if [ $(($throttled_dec & 0x10000)) -ne 0 ]; then
        echo "      ⚠️  曾经出现欠压"
    fi
    if [ $(($throttled_dec & 0x20000)) -ne 0 ]; then
        echo "      ⚠️  曾经频率受限"
    fi
    if [ $(($throttled_dec & 0x40000)) -ne 0 ]; then
        echo "      ⚠️  曾经过热限流"
    fi
fi

# 2. CPU 状态
echo -e "\n📊 CPU 状态:"
temp=$(vcgencmd measure_temp)
freq=$(vcgencmd measure_clock arm)
freq_mhz=$((${freq#*=} / 1000000))
volt=$(vcgencmd measure_volts core)

echo "   温度: $temp"
echo "   CPU 频率: ${freq_mhz} MHz"
echo "   核心电压: $volt"

# 评估频率
if [ $freq_mhz -ge 1500 ]; then
    echo "   ✅ CPU 频率正常 (${freq_mhz} MHz)"
elif [ $freq_mhz -ge 1200 ]; then
    echo "   ⚠️  CPU 频率偏低 (${freq_mhz} MHz)，但可接受"
else
    echo "   ❌ CPU 频率过低 (${freq_mhz} MHz)"
    echo "   💡 可能需要手动设置 performance 模式"
fi

# 3. 内存状态
echo -e "\n💾 内存状态:"
free -h | grep "Mem:"
gpu_mem=$(vcgencmd get_mem gpu | cut -d= -f2)
echo "   GPU 内存: $gpu_mem"

# 4. CPU 调速器
echo -e "\n⚙️  CPU 调速器:"
for cpu in /sys/devices/system/cpu/cpu[0-3]; do
    if [ -e $cpu/cpufreq/scaling_governor ]; then
        governor=$(cat $cpu/cpufreq/scaling_governor)
        min_freq=$(cat $cpu/cpufreq/scaling_min_freq)
        max_freq=$(cat $cpu/cpufreq/scaling_max_freq)
        min_mhz=$((min_freq / 1000))
        max_mhz=$((max_freq / 1000))
        echo "   ${cpu##*/}: $governor (${min_mhz}-${max_mhz} MHz)"
    fi
done

# 5. 性能测试建议
echo -e "\n============================================================"
echo "📝 下一步操作:"
echo "============================================================"

if [ $freq_mhz -ge 1400 ]; then
    echo "✅ 系统状态良好，可以直接测试推理性能"
    echo ""
    echo "运行以下命令:"
    echo "  cd ~/Desktop/rmyc-raspi-framework"
    echo "  source venv/bin/activate"
    echo "  python test_onnx_performance.py"
else
    echo "⚠️  CPU 频率仍然较低，建议先优化"
    echo ""
    echo "运行以下命令:"
    echo "  sudo bash tools/fix_cpu_performance.sh"
fi

echo "============================================================"
