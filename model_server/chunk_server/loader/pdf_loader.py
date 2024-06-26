from typing import List

import pdfplumber
from langchain_core.documents import Document
from loguru import logger
from tqdm import tqdm


class PDFLoader:

    def __init__(self, file_path):
        self.file_path = file_path

    def table_to_markdown(self, table: List[List[str]]) -> str:
        # 清理数据并创建Markdown表格
        markdown_table = "| " + " | ".join(
            (cell or "").replace("\n", " ") for cell in table[0]) + " |\n"  # table headers
        markdown_table += "|---" * len(table[0]) + "|\n"  # table header-row separator

        for row in table[1:]:
            markdown_table += "| " + " | ".join(
                (cell or "").replace("\n", " ") if cell else "" for cell in row) + " |\n"

        return markdown_table

    def load(self) -> List[Document]:

        table_docs = []
        text_docs = []

        with pdfplumber.open(self.file_path) as pdf:
            # 解析文本
            for page in tqdm(pdf.pages, desc=f"解析PDF文本[{self.file_path}]"):
                raw_text = page.extract_text().replace("\n", " ").strip()
                text_docs.append(Document(raw_text))

            # 解析表格
            for page in tqdm(pdf.pages, desc=f"解析PDF表格[{self.file_path}]"):
                table_list = page.extract_tables()
                for table in table_list:
                    if table is not None:
                        # 如果表格的所有单元格都为空或None，跳过这个表格
                        if all(not cell or cell.isspace() for row in table for cell in row):
                            continue
                        table_docs.append(Document(self.table_to_markdown(table), metadata={"format": "table"}))

            logger.info(f'解析PDF文件完成：{self.file_path}')

        return text_docs + table_docs
