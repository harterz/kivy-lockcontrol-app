#!/bin/bash

# APK构建脚本
echo "开始构建APK..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装。请先安装Docker。"
    echo "macOS安装: https://docs.docker.com/desktop/mac/install/"
    exit 1
fi

# 构建Docker镜像
echo "构建Docker镜像..."
docker build -t kivy-apk-builder .

# 运行容器并构建APK
echo "在Docker容器中构建APK..."
docker run --rm -v $(pwd):/app kivy-apk-builder

echo "APK构建完成！"
echo "APK文件位置: ./bin/myapp-0.1-arm64-v8a_armeabi-v7a-debug.apk"