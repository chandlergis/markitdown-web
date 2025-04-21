import streamlit as st
import os
import zipfile
import tempfile
import io
from pathlib import Path
from markitdown import MarkItDown

st.set_page_config(page_title="MarkItDown Web", layout="wide")

st.title("MarkItDown Web 转换器")
st.info("提示：要处理整个文件夹，请先将其压缩为 ZIP 文件，然后上传该 ZIP 文件。")

# Initialize MarkItDown without the enable_plugins parameter
# Consider initializing *inside* the processing loop if memory is a concern
# for very large batches, but generally initializing once is fine.
try:
    md = MarkItDown()
    # List supported extensions for filtering within ZIP files
    # You might need to refine this list based on MarkItDown's actual capabilities
    # and potentially add more specific checks later if needed.
    SUPPORTED_EXTENSIONS = (
        '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif',
        '.mp3', '.wav', '.ogg', '.flac',  # Add audio extensions MarkItDown supports
        '.html', '.htm',
        '.csv', '.json', '.xml',
        # MarkItDown might handle these internally, but we list them for clarity
    )
except Exception as e:
    st.error(f"初始化 MarkItDown 失败: {e}")
    st.stop() # Stop execution if MarkItDown can't initialize


# --- Function to process a single file ---
def process_single_file(uploaded_file):
    st.subheader(f"处理单个文件: {uploaded_file.name}")
    temp_path = f"temp_{uploaded_file.name}" # Using simple temp names, consider tempfile module for robustness
    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert file
        st.write(f"正在转换 {uploaded_file.name}...")
        with st.spinner('转换进行中...'):
            result = md.convert(temp_path)

        # Display conversion result
        st.text_area(f"'{uploaded_file.name}' 的转换结果", result.text_content, height=300, key=f"text_{uploaded_file.name}")

        # Provide download button
        output_filename = f"{Path(uploaded_file.name).stem}.md"
        st.download_button(
            label=f"下载 {output_filename}",
            data=result.text_content,
            file_name=output_filename,
            mime="text/markdown",
            key=f"download_{uploaded_file.name}"
        )
        st.success(f"文件 '{uploaded_file.name}' 转换成功！")

    except Exception as e:
        st.error(f"文件 '{uploaded_file.name}' 转换失败: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e_clean:
                st.warning(f"无法删除临时文件 {temp_path}: {e_clean}")

# --- Function to process a ZIP file ---
def process_zip_file(uploaded_file):
    st.subheader(f"处理文件夹 (来自 ZIP 文件): {uploaded_file.name}")
    results = {} # Store results: {relative_path: markdown_content}
    errors = {} # Store errors: {relative_path: error_message}
    processed_files_count = 0
    skipped_files_count = 0

    temp_dir = None # Initialize temp_dir to None
    zip_temp_path = f"temp_{uploaded_file.name}"

    try:
        # Save uploaded zip file temporarily
        with open(zip_temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            st.write(f"正在解压 {uploaded_file.name}...")
            try:
                with zipfile.ZipFile(zip_temp_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                st.write("解压完成，开始处理文件...")
            except zipfile.BadZipFile:
                st.error(f"文件 '{uploaded_file.name}' 不是有效的 ZIP 文件或已损坏。")
                return # Stop processing this file
            except Exception as e_extract:
                st.error(f"解压 '{uploaded_file.name}' 时出错: {e_extract}")
                return # Stop processing this file

            # Recursively process files in the extracted directory
            base_path = Path(temp_dir)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Count total files first for progress bar (optional but nice)
            total_files = sum(1 for item in base_path.rglob('*') if item.is_file())
            files_processed_so_far = 0

            for item_path in base_path.rglob('*'):
                if item_path.is_file():
                    relative_path = item_path.relative_to(base_path)
                    file_ext = item_path.suffix.lower()
                    status_text.text(f"处理中: {relative_path} ({files_processed_so_far + 1}/{total_files})")

                    # Check if the file type is likely supported
                    if file_ext in SUPPORTED_EXTENSIONS:
                        try:
                            # Convert file
                            with st.spinner(f'转换 {relative_path}...'):
                                result = md.convert(str(item_path))
                            
                            output_md_path = relative_path.with_suffix('.md')
                            results[str(output_md_path)] = result.text_content
                            processed_files_count += 1
                        except Exception as e:
                            errors[str(relative_path)] = str(e)
                            st.warning(f"转换文件 '{relative_path}' 失败: {e}")
                        finally:
                            files_processed_so_far += 1
                            progress_bar.progress(files_processed_so_far / total_files if total_files > 0 else 1)
                    else:
                        # Optionally log skipped files
                        # st.write(f"跳过不支持的文件类型: {relative_path}")
                        skipped_files_count += 1
                        files_processed_so_far += 1
                        progress_bar.progress(files_processed_so_far / total_files if total_files > 0 else 1)
            
            status_text.text(f"处理完成！共处理 {total_files} 个文件。")
            progress_bar.progress(1.0) # Ensure progress bar completes


        # --- Create result ZIP ---
        if results:
            st.write(f"成功转换 {processed_files_count} 个文件。")
            if skipped_files_count > 0:
                st.write(f"跳过 {skipped_files_count} 个不支持或无法处理的文件。")

            # Create zip in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                for md_path, md_content in results.items():
                    # Ensure content is bytes
                    if isinstance(md_content, str):
                       md_content_bytes = md_content.encode('utf-8')
                    else:
                       md_content_bytes = md_content # Assume it's already bytes if not str
                    zip_out.writestr(md_path, md_content_bytes)

            zip_buffer.seek(0)

            # Provide download button for the results zip
            output_zip_filename = f"{Path(uploaded_file.name).stem}_markdown_results.zip"
            st.download_button(
                label=f"下载包含 {processed_files_count} 个 Markdown 文件的 ZIP 压缩包",
                data=zip_buffer,
                file_name=output_zip_filename,
                mime="application/zip",
                key=f"download_zip_{uploaded_file.name}"
            )
        else:
            st.warning(f"在 '{uploaded_file.name}' 中没有找到可成功转换的文件。")

        if errors:
            st.error("转换过程中出现以下错误：")
            error_details = "\n".join([f"- {path}: {msg}" for path, msg in errors.items()])
            st.text_area("错误详情", error_details, height=150, key=f"errors_{uploaded_file.name}")

    except Exception as e:
        st.error(f"处理 ZIP 文件 '{uploaded_file.name}' 时发生意外错误: {str(e)}")
    finally:
        # Clean up temporary zip file
        if os.path.exists(zip_temp_path):
             try:
                 os.remove(zip_temp_path)
             except Exception as e_clean:
                 st.warning(f"无法删除临时 ZIP 文件 {zip_temp_path}: {e_clean}")
        # The temporary directory 'temp_dir' is automatically cleaned up by the 'with' statement


# --- Main App Logic ---
uploaded_files = st.file_uploader(
    "选择要转换的文件 (单个文件或包含文件夹内容的 ZIP 文件)",
    accept_multiple_files=True,
    # You might want to add '.zip' to the type list if you want browser filtering,
    # but checking the name after upload is more robust.
    # type=['pdf', 'docx', 'pptx', 'xlsx', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'mp3', 'wav', 'html', 'csv', 'json', 'xml', 'zip']
)

if uploaded_files:
    st.markdown("---") # Separator

    for uploaded_file in uploaded_files:
        file_name_lower = uploaded_file.name.lower()

        if file_name_lower.endswith('.zip'):
            process_zip_file(uploaded_file)
        elif any(file_name_lower.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
             process_single_file(uploaded_file)
        else:
            st.warning(f"跳过文件 '{uploaded_file.name}'：文件类型不支持或无法识别。仅支持处理单个受支持文件或包含受支持文件的 ZIP 压缩包。")

        st.markdown("---") # Separator between file results


st.sidebar.markdown("""
## 使用说明
1.  **上传文件:** 点击"选择要转换的文件"
    *   上传一个或多个 **单个文件** (PDF, Word, 图片等)。
    *   或者，上传一个 **ZIP 压缩文件**，其中包含您想批量处理的文件夹内容。
2.  **自动转换:** 系统会根据上传类型进行处理：
    *   **单个文件:** 直接转换为 Markdown。
    *   **ZIP 文件:** 解压 ZIP 文件，并尝试转换其中所有支持的文件类型。
3.  **预览结果:**
    *   **单个文件:** 直接在页面上预览 Markdown 文本。
    *   **ZIP 文件:** 显示处理摘要（成功/失败数量）。
4.  **下载结果:**
    *   **单个文件:** 点击对应的 "下载 Markdown 文件" 按钮。
    *   **ZIP 文件:** 点击 "下载包含 ... 个 Markdown 文件的 ZIP 压缩包" 按钮，获取一个包含所有转换结果的新 ZIP 文件（保留原目录结构）。

## 支持的文件格式 (在 ZIP 包内或单独上传)
- PDF (.pdf)
- Word (.doc, .docx)
- PowerPoint (.ppt, .pptx)
- Excel (.xls, .xlsx)
- 图片文件 (.png, .jpg, .jpeg, .gif, .bmp, .tiff)
- 音频文件 (如 .mp3, .wav - 取决于 MarkItDown 配置)
- HTML (.html, .htm)
- CSV, JSON, XML (.csv, .json, .xml)
- **ZIP 文件 (.zip)** 用于批量处理文件夹内容
""")