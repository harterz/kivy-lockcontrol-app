# APK构建指南

由于本地buildozer编译遇到了一些环境配置问题，我为您提供了几种替代解决方案来构建APK文件：

## 方案一：使用Docker构建（推荐）

### 前提条件
1. 安装Docker Desktop for Mac
   - 下载地址：https://docs.docker.com/desktop/mac/install/
   - 安装完成后启动Docker Desktop

### 构建步骤
1. 确保Docker正在运行
2. 在终端中运行：
   ```bash
   ./build_apk.sh
   ```
3. 等待构建完成，APK文件将生成在 `bin/` 目录下

## 方案二：使用GitHub Actions在线构建

### 步骤
1. 将项目上传到GitHub仓库
2. 在仓库中创建 `.github/workflows/build-apk.yml` 文件
3. GitHub Actions会自动构建APK并提供下载

### GitHub Actions配置文件内容：
```yaml
name: Build APK
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install buildozer cython
    - name: Build APK
      run: buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: apk
        path: bin/*.apk
```

## 方案三：使用在线构建服务

### Replit
1. 访问 https://replit.com
2. 创建新项目，上传代码
3. 安装buildozer并构建

### Google Colab
1. 访问 https://colab.research.google.com
2. 创建新笔记本
3. 上传代码并运行构建命令

## 方案四：本地环境修复

如果您想继续使用本地环境，可以尝试：

1. 重新安装buildozer：
   ```bash
   pip uninstall buildozer
   pip install buildozer
   ```

2. 检查Java版本（需要Java 8）：
   ```bash
   java -version
   ```

3. 清理并重新构建：
   ```bash
   buildozer android clean
   buildozer android debug
   ```

## 当前项目文件

- `main_minimal.py` - 最简化的Kivy应用
- `buildozer.spec` - 已优化的构建配置
- `Dockerfile` - Docker构建配置
- `build_apk.sh` - 自动化构建脚本

## 推荐方案

建议使用**方案一（Docker构建）**，因为：
- 环境隔离，避免本地配置问题
- 构建环境标准化
- 成功率高
- 可重复构建

如果您没有Docker，推荐使用**方案二（GitHub Actions）**，完全在线构建，无需本地环境配置。