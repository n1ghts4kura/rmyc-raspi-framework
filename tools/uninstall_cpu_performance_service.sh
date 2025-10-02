#!/bin/bash
#
# uninstall_cpu_performance_service.sh
# 
# 功能：卸载 CPU 性能模式自启服务，恢复节能模式
# 用法：sudo bash tools/uninstall_cpu_performance_service.sh
#

echo "============================================================"
echo "🗑️  CPU 性能模式服务卸载工具"
echo "============================================================"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 错误：需要 root 权限"
    echo "请使用：sudo bash $0"
    exit 1
fi

SERVICE_FILE="/etc/systemd/system/cpu-performance.service"

# 1. 停止服务
echo "⏹️  停止服务..."
systemctl stop cpu-performance.service 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 服务已停止"
else
    echo "⚠️  服务可能未运行"
fi

echo ""

# 2. 禁用开机自启
echo "🚫 禁用开机自启..."
systemctl disable cpu-performance.service 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 开机自启已禁用"
else
    echo "⚠️  服务可能未启用"
fi

echo ""

# 3. 删除服务文件
echo "🗑️  删除服务文件..."
if [ -f "$SERVICE_FILE" ]; then
    rm "$SERVICE_FILE"
    echo "✅ 服务文件已删除: $SERVICE_FILE"
else
    echo "⚠️  服务文件不存在"
fi

echo ""

# 4. 重载 systemd 配置
echo "🔄 重载 systemd 配置..."
systemctl daemon-reload
echo "✅ systemd 配置已重载"

echo ""

# 5. 恢复节能模式
echo "💤 恢复节能模式 (ondemand)..."
echo ondemand | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null
sleep 1
echo "✅ CPU 调度器已恢复为 ondemand（节能模式）"

echo ""

# 6. 验证状态
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
echo "============================================================"
echo "✅ 卸载完成！"
echo "============================================================"
echo ""
echo "💡 提示："
echo "  - CPU 已恢复节能模式，空闲时会降至 600 MHz"
echo "  - 如需重新启用性能模式，请运行："
echo "    sudo bash tools/set_cpu_performance.sh"
echo "  - 如需重新安装自启服务，请运行："
echo "    sudo bash tools/install_cpu_performance_service.sh"
echo "============================================================"
