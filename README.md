
# MarkItDown Web 转换器

一个基于 MarkItDown 的 Web 界面工具，提供便捷的文件转 Markdown 功能。

## 功能特点

- 🚀 简单易用的 Web 界面
- 📦 支持批量文件上传和转换
- 👀 实时预览转换结果
- 💾 一键下载转换后的文件
- 🔌 支持多种文件格式转换

## 支持的文件格式

- 文档类
  - PDF 文件
  - Microsoft Word 文档
  - PowerPoint 演示文稿
  - Excel 表格

- 多媒体
  - 图片文件（支持 EXIF 元数据和 OCR）
  - 音频文件（支持 EXIF 元数据和语音转写）

- 其他格式
  - HTML 网页
  - CSV 数据文件
  - JSON 文件
  - XML 文档
  - ZIP 压缩包（可遍历内容）

## 环境要求

- Python 3.x
- pip 包管理器

## 快速开始

1. 克隆项目到本地：
```bash
git clone git@github.com:ccbsdu/markitdown-web.git
cd markitdown-web
```

2. 创建并激活虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

4. 启动应用：
```bash
streamlit run app.py
```

5. 在浏览器中访问应用（默认地址：http://localhost:8501）

## docker启动
运行以下命令来构建镜像：
```bash
docker build -t markitdown-web-app .
```
docker运行
```bash
docker run -d -p 8501:8501 --name markitdown_web_container --restart unless-stopped markitdown-web-app
```
## 使用说明

1. 打开应用后，点击"选择要转换的文件"按钮或直接拖拽文件到上传区域
2. 支持同时选择多个文件进行批量转换
3. 文件上传后会自动开始转换
4. 转换完成后可以在界面上预览转换结果
5. 点击"下载 Markdown 文件"按钮保存转换后的文件

## 项目结构

```
markitdown-web/
├── app.py            # 主应用程序
├── requirements.txt  # 项目依赖
└── README.md        # 项目文档
```

## 注意事项

- 建议使用虚拟环境运行应用
- 大文件转换可能需要较长时间，请耐心等待
- 转换后的临时文件会自动清理
- 请确保有足够的磁盘空间

## 许可证

本项目基于 MIT 许可证开源。

## 致谢

- 感谢 [MarkItDown](https://github.com/microsoft/markitdown) 提供核心转换功能
- 感谢 [Streamlit](https://streamlit.io/) 提供优秀的 Web 框架
```
