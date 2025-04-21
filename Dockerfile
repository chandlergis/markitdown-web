# 使用官方 Python 3.10 slim 版本作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
# 单独复制 requirements.txt 可以利用 Docker 的层缓存机制
# 只有当 requirements.txt 改变时，下面的 RUN 命令才会重新执行
COPY requirements.txt ./

# 安装系统依赖 (如果需要的话，例如某些库可能需要 build-essential 或其他库)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     some-system-dependency \
#     && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
# --no-cache-dir 减少镜像大小
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
COPY . .

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 设置容器启动时执行的命令
# 使用 --server.address 0.0.0.0 使 Streamlit 服务可以从容器外部访问
# 使用 --server.enableCORS=false 和 --server.enableXsrfProtection=false
# 在某些代理/部署环境下可能需要，但请注意安全含义。可以先不加。
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]