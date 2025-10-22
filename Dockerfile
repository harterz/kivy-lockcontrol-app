# Dockerfile for building Android APK with Kivy
FROM ubuntu:20.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-8-jdk \
    wget \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    libncurses5-dev \
    libsqlite3-dev \
    libreadline-dev \
    libbz2-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装Python依赖
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install buildozer cython

# 安装Android SDK
RUN mkdir -p ${ANDROID_HOME} && \
    cd ${ANDROID_HOME} && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip && \
    unzip commandlinetools-linux-7583922_latest.zip && \
    rm commandlinetools-linux-7583922_latest.zip

# 构建APK
CMD ["buildozer", "android", "debug"]