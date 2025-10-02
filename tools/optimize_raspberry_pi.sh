#!/bin/bash
################################################################################
# 树莓派 4B 性能优化一键脚本
# 用途：自动应用所有系统级优化，提升 YOLO 推理性能
# 使用：sudo bash tools/optimize_raspberry_pi.sh
################################################################################

set -e  # 遇到错误立即退出

echo "=================================="
echo "树莓派 4B 性能优化脚本"
echo "=================================="
echo ""

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    echo "   sudo bash tools/optimize_raspberry_pi.sh"
    exit 1
fi

echo "📋 优化清单："
echo "  1. 增加 GPU 内存分配（64MB → 256MB）"
echo "  2. CPU 超频（1.5GHz → 1.8GHz）"
echo "  3. GPU 超频（500MHz → 600MHz）"
echo "  4. 禁用蓝牙和不必要服务"
echo "  5. 设置性能调度器"
echo "  6. 优化 Python 环境变量"
echo ""

read -p "⚠️  是否继续？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消优化"
    exit 0
fi

# 备份配置文件
echo "🔖 备份配置文件..."
cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)
cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)

# ============================================================================
# 1. 优化 /boot/config.txt
# ============================================================================
echo "⚙️  配置 /boot/config.txt..."

# 检查是否已存在优化配置
if grep -q "# RMYC Performance Optimization" /boot/config.txt; then
    echo "   ⚠️  检测到已存在优化配置，跳过"
else
    cat >> /boot/config.txt << 'EOF'

# ============================================================================
# RMYC Performance Optimization
# 添加时间: $(date)
# ============================================================================

[all]
# GPU 内存分配（提升视觉处理性能）
gpu_mem=256

# CPU 超频（1.5GHz → 1.8GHz）
over_voltage=4
arm_freq=1800

# GPU 超频（500MHz → 600MHz）
gpu_freq=600

# 内存超频
sdram_freq=3200

# 温度限制（保护硬件）
temp_limit=80

# 启用硬件视频加速
dtoverlay=vc4-fkms-v3d
max_framebuffers=2

EOF
    echo "   ✅ /boot/config.txt 配置完成"
fi

# ============================================================================
# 2. 禁用不必要的系统服务
# ============================================================================
echo "🔧 禁用不必要的系统服务..."

# 禁用蓝牙
systemctl disable bluetooth 2>/dev/null || true
systemctl stop bluetooth 2>/dev/null || true
echo "   ✅ 蓝牙已禁用"

# 禁用 WiFi（如果使用有线网络）
read -p "   ⚠️  是否禁用 WiFi？(仅在使用有线网络时) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl disable wpa_supplicant 2>/dev/null || true
    systemctl stop wpa_supplicant 2>/dev/null || true
    echo "   ✅ WiFi 已禁用"
fi

# 禁用图形界面（可选）
read -p "   ⚠️  是否禁用图形界面？(释放更多资源) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl set-default multi-user.target
    echo "   ✅ 图形界面已禁用（下次启动生效）"
fi

# ============================================================================
# 3. 设置 CPU 性能调度器
# ============================================================================
echo "⚡ 设置 CPU 性能调度器..."

# 安装 cpufrequtils
apt-get install -y cpufrequtils 2>/dev/null || true

# 设置所有核心为性能模式
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -f "$cpu/cpufreq/scaling_governor" ]; then
        echo "performance" > "$cpu/cpufreq/scaling_governor"
    fi
done

# 持久化配置
cat > /etc/default/cpufrequtils << EOF
GOVERNOR="performance"
EOF

echo "   ✅ CPU 调度器设置为性能模式"

# ============================================================================
# 4. 优化 Python 环境变量
# ============================================================================
echo "🐍 配置 Python 性能环境变量..."

# 检查当前用户的 .bashrc
USER_HOME=$(eval echo ~${SUDO_USER})
BASHRC_FILE="$USER_HOME/.bashrc"

if grep -q "# RMYC Python Optimization" "$BASHRC_FILE"; then
    echo "   ⚠️  检测到已存在 Python 优化配置，跳过"
else
    cat >> "$BASHRC_FILE" << 'EOF'

# ============================================================================
# RMYC Python Optimization
# ============================================================================
export OMP_NUM_THREADS=4              # OpenMP 线程数
export OPENBLAS_NUM_THREADS=4         # BLAS 库线程数
export MKL_NUM_THREADS=4              # Intel MKL 线程数
export NUMEXPR_NUM_THREADS=4          # NumPy 表达式线程数
export PYTHONOPTIMIZE=2               # 启用优化模式

EOF
    echo "   ✅ Python 环境变量配置完成"
fi

# ============================================================================
# 5. 安装性能监控工具
# ============================================================================
echo "📊 安装性能监控工具..."
apt-get install -y htop 2>/dev/null || true
echo "   ✅ 已安装 htop（使用 'htop' 命令监控系统）"

# ============================================================================
# 6. 创建性能测试脚本
# ============================================================================
echo "🔍 创建性能测试脚本..."

cat > /usr/local/bin/check_rpi_perf << 'EOF'
#!/bin/bash
# 快速查看树莓派性能状态

echo "=================================="
echo "树莓派性能状态"
echo "=================================="
echo "⏰ 当前时间: $(date)"
echo ""
echo "📊 CPU 信息"
echo "  - 频率: $(vcgencmd measure_clock arm | awk -F= '{printf "%.0f MHz\n", $2/1000000}')"
echo "  - 温度: $(vcgencmd measure_temp | awk -F= '{print $2}')"
echo "  - 调度器: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
echo ""
echo "🎮 GPU 信息"
echo "  - 频率: $(vcgencmd measure_clock core | awk -F= '{printf "%.0f MHz\n", $2/1000000}')"
echo "  - 内存: $(vcgencmd get_mem gpu | awk -F= '{print $2}')"
echo ""
echo "💾 内存信息"
free -h | grep Mem | awk '{printf "  - 总计: %s | 已用: %s | 可用: %s\n", $2, $3, $7}'
echo ""
echo "⚡ 电源状态"
vcgencmd get_throttled | awk -F= '{
    val=$2
    if (val == "0x0") {
        print "  - ✅ 正常（无欠压/过热）"
    } else {
        print "  - ⚠️  异常码: " val
    }
}'
echo "=================================="
EOF

chmod +x /usr/local/bin/check_rpi_perf
echo "   ✅ 已创建性能检查脚本（使用 'check_rpi_perf' 命令）"

# ============================================================================
# 完成
# ============================================================================
echo ""
echo "=================================="
echo "✅ 优化完成！"
echo "=================================="
echo ""
echo "📝 下一步操作："
echo "  1. 重启树莓派生效：sudo reboot"
echo "  2. 重启后检查状态：check_rpi_perf"
echo "  3. 运行性能测试：python test_annotation.py"
echo ""
echo "🔧 如需回滚："
echo "  - 恢复 /boot/config.txt："
echo "    sudo cp /boot/config.txt.backup.* /boot/config.txt"
echo "  - 恢复 .bashrc："
echo "    cp ~/.bashrc.backup.* ~/.bashrc"
echo ""
echo "⚠️  注意事项："
echo "  - 超频可能导致发热，请确保散热良好"
echo "  - 如遇到系统不稳定，降低 arm_freq 到 1750 或 1700"
echo "  - 监控温度，超过 75°C 时考虑加装风扇"
echo ""

read -p "是否立即重启？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 正在重启..."
    sleep 2
    reboot
else
    echo "👋 请稍后手动重启：sudo reboot"
fi
