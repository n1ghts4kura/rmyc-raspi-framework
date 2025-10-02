#!/bin/bash
# GPU 诊断工具

echo "============================================================"
echo "🔍 树莓派 GPU 诊断工具"
echo "============================================================"

echo -e "\n📌 1. 系统信息"
echo "----------------------------"
uname -a
echo "CPU: $(lscpu | grep 'Model name' | cut -d: -f2 | xargs)"
echo "内存: $(free -h | grep Mem | awk '{print $2}')"

echo -e "\n📌 2. GPU 配置 (/boot/firmware/config.txt)"
echo "----------------------------"
grep -E "gpu_mem|dtoverlay|max_framebuffers|dtparam=spi" /boot/firmware/config.txt | grep -v "^#"

echo -e "\n📌 3. 当前显示驱动"
echo "----------------------------"
lsmod | grep -E "vc4|v3d|fbtft|waveshare"

echo -e "\n📌 4. Vulkan 设备"
echo "----------------------------"
vulkaninfo --summary 2>/dev/null | grep -A 5 "GPU"

echo -e "\n📌 5. /dev/dri 设备"
echo "----------------------------"
ls -lh /dev/dri/

echo -e "\n📌 6. V3D GPU 状态"
echo "----------------------------"
if [ -e /sys/kernel/debug/dri/0/v3d_ident ]; then
    sudo cat /sys/kernel/debug/dri/0/v3d_ident 2>/dev/null || echo "需要 root 权限访问"
else
    echo "⚠️  V3D 调试接口不存在"
fi

echo -e "\n📌 7. GPU 进程监控"
echo "----------------------------"
echo "运行以下命令监控 GPU 使用率:"
echo "  watch -n 1 'vcgencmd get_mem gpu && sudo cat /sys/kernel/debug/dri/0/v3d_stats 2>/dev/null'"

echo -e "\n📌 8. Vulkan ICD 配置"
echo "----------------------------"
ls -lh /usr/share/vulkan/icd.d/
cat /usr/share/vulkan/icd.d/broadcom_icd.aarch64.json 2>/dev/null || echo "❌ broadcom_icd.aarch64.json 不存在"

echo -e "\n📌 9. 当前帧缓冲设备"
echo "----------------------------"
ls -lh /dev/fb*

echo -e "\n============================================================"
echo "💡 建议检查项："
echo "  1. 确认没有加载 fbtft/waveshare 驱动 (lsmod)"
echo "  2. 确认 dtoverlay=vc4-kms-v3d 已启用"
echo "  3. 确认 /dev/dri/card0 和 renderD128 存在"
echo "  4. 重启后测试（确保驱动正确加载）"
echo "============================================================"
