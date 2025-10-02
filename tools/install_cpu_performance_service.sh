#!/bin/bash
#
# install_cpu_performance_service.sh
# 
# 功能：安装开机自启的 CPU 性能模式服务
# 用法：sudo bash tools/install_cpu_performance_service.sh
#

echo "============================================================"
echo "🔧 CPU 性能模式自启服务安装工具"
echo "============================================================"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 错误：需要 root 权限"
    echo "请使用：sudo bash $0"
    exit 1
fi

# 1. 创建 systemd 服务文件
SERVICE_FILE="/etc/systemd/system/cpu-performance.service"

echo "📝 正在创建 systemd 服务文件..."
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Set CPU Governor to Performance Mode
Documentation=https://github.com/n1ghts4kura/rmyc-raspi-framework
After=multi-user.target
Before=graphical.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null'
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

if [ $? -eq 0 ]; then
    echo "✅ 服务文件已创建: $SERVICE_FILE"
else
    echo "❌ 服务文件创建失败"
    exit 1
fi

echo ""

# 2. 重载 systemd 配置
echo "🔄 重载 systemd 配置..."
systemctl daemon-reload
if [ $? -eq 0 ]; then
    echo "✅ systemd 配置已重载"
else
    echo "❌ systemd 配置重载失败"
    exit 1
fi

echo ""

# 3. 启用服务（开机自启）
echo "🚀 启用开机自启..."
systemctl enable cpu-performance.service
if [ $? -eq 0 ]; then
    echo "✅ 服务已设置为开机自启"
else
    echo "❌ 服务启用失败"
    exit 1
fi

echo ""

# 4. 立即启动服务（非阻塞）
echo "⚡ 立即启动服务..."
systemctl start cpu-performance.service --no-block
sleep 2
if systemctl is-active --quiet cpu-performance.service; then
    echo "✅ 服务已启动"
else
    echo "⚠️  服务启动状态未知，继续检查..."
fi

echo ""

# 5. 验证服务状态
echo "📊 验证服务状态："
echo "------------------------------------------------------------"
systemctl status cpu-performance.service --no-pager -l || true

echo ""
echo "------------------------------------------------------------"

# 6. 验证 CPU 状态
echo ""
echo "📊 当前 CPU 状态："
echo "------------------------------------------------------------"
echo "调度器模式: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
echo "CPU 频率:"
for i in 0 1 2 3; do
    freq=$(cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_cur_freq)
    mhz=$(echo "scale=1; $freq/1000" | bc)
    echo "  CPU $i: $mhz MHz"
done
echo "温度: $(vcgencmd measure_temp)"

echo ""

# 7. 完成提示
echo "============================================================"
echo "✅ 安装完成！"
echo "============================================================"
echo ""
echo "📋 服务管理命令："
echo "------------------------------------------------------------"
echo "查看服务状态："
echo "  sudo systemctl status cpu-performance.service"
echo ""
echo "停止服务（恢复节能模式）："
echo "  sudo systemctl stop cpu-performance.service"
echo ""
echo "禁用开机自启："
echo "  sudo systemctl disable cpu-performance.service"
echo ""
echo "重新启动服务："
echo "  sudo systemctl restart cpu-performance.service"
echo ""
echo "查看服务日志："
echo "  sudo journalctl -u cpu-performance.service"
echo ""
echo "卸载服务："
echo "  sudo bash tools/uninstall_cpu_performance_service.sh"
echo "============================================================"
echo ""
echo "⚠️  注意："
echo "  - 性能模式会略微增加功耗（约 1-2W）"
echo "  - 温度会比节能模式高 5-10°C"
echo "  - 确保使用 5V 3A 电源供电"
echo "  - 建议添加散热片或风扇"
echo "============================================================"
