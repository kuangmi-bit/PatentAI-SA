"""
Batch import service for patents
Supports importing multiple patents from various sources
"""
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from app.core.logging import get_logger
from app.services.db_service import PatentService, LibraryService
from app.services.zhipu_client import PatentEmbedder, ZhipuClient

logger = get_logger(__name__)


class BatchImportService:
    """批量导入服务"""
    
    def __init__(self):
        self.embedder = PatentEmbedder(ZhipuClient())
    
    async def import_from_json(
        self,
        library_id: str,
        json_data: List[Dict[str, Any]],
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        从 JSON 数据批量导入专利
        
        Args:
            library_id: 目标专利库ID
            json_data: 专利数据列表
            generate_embeddings: 是否生成嵌入向量
            
        Returns:
            导入结果统计
        """
        results = {
            "total": len(json_data),
            "success": 0,
            "failed": 0,
            "errors": [],
            "patent_ids": []
        }
        
        # 验证库存在
        library = await LibraryService.get_library(library_id)
        if not library:
            raise ValueError(f"Library {library_id} not found")
        
        for idx, patent_data in enumerate(json_data):
            try:
                # 处理 inventors 字段（支持字符串或列表）
                inventors = patent_data.get("inventors")
                if isinstance(inventors, list):
                    inventors = ", ".join(inventors)
                
                # 处理 claims 字段（支持字符串或列表）
                claims = patent_data.get("claims")
                if isinstance(claims, list):
                    claims = "\n\n".join(claims)
                
                # 创建专利
                patent = await PatentService.create_patent(
                    library_id=library_id,
                    title=patent_data.get("title", "Untitled"),
                    application_no=patent_data.get("application_no"),
                    publication_no=patent_data.get("publication_no"),
                    ipc=patent_data.get("ipc"),
                    applicant=patent_data.get("applicant"),
                    inventors=inventors,
                    abstract=patent_data.get("abstract"),
                    claims=claims,
                    description=patent_data.get("description"),
                    file_path=patent_data.get("file_path"),
                    quality_score=patent_data.get("quality_score", 80)
                )
                
                results["success"] += 1
                results["patent_ids"].append(patent.id)
                
                # 异步生成嵌入向量
                if generate_embeddings:
                    asyncio.create_task(
                        self._generate_embedding_async(patent.id, patent_data)
                    )
                
                logger.info(f"Imported patent {idx+1}/{len(json_data)}: {patent.id}")
                
            except Exception as e:
                results["failed"] += 1
                error_msg = f"Row {idx+1}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(f"Failed to import patent at row {idx+1}", error=str(e))
        
        # 更新库统计
        await LibraryService.update_patent_count(library_id)
        
        logger.info(
            f"Batch import completed",
            library_id=library_id,
            total=results["total"],
            success=results["success"],
            failed=results["failed"]
        )
        
        return results
    
    async def _generate_embedding_async(self, patent_id: str, patent_data: Dict[str, Any]):
        """异步生成嵌入向量"""
        try:
            # 构建专利文本
            text_parts = []
            if patent_data.get("title"):
                text_parts.append(f"标题: {patent_data['title']}")
            if patent_data.get("abstract"):
                text_parts.append(f"摘要: {patent_data['abstract']}")
            if patent_data.get("claims"):
                if isinstance(patent_data["claims"], list):
                    text_parts.append(f"权利要求: {' '.join(patent_data['claims'])}")
                else:
                    text_parts.append(f"权利要求: {patent_data['claims']}")
            
            full_text = "\n".join(text_parts)
            
            # 生成嵌入
            embedding = await self.embedder.embed_text(full_text)
            
            # 更新数据库
            await PatentService.update_embedding(
                patent_id=patent_id,
                embedding=embedding,
                dimensions=len(embedding)
            )
            
            logger.info(f"Embedding generated for patent {patent_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for {patent_id}", error=str(e))
    
    async def import_from_directory(
        self,
        library_id: str,
        directory_path: str,
        file_pattern: str = "*.json",
        generate_embeddings: bool = True
    ) -> Dict[str, Any]:
        """
        从目录批量导入 JSON 文件
        
        Args:
            library_id: 目标专利库ID
            directory_path: 目录路径
            file_pattern: 文件匹配模式
            generate_embeddings: 是否生成嵌入向量
            
        Returns:
            导入结果统计
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        all_results = {
            "files_processed": 0,
            "total_patents": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        # 查找所有匹配的文件
        json_files = list(directory.glob(file_pattern))
        
        for json_file in json_files:
            try:
                logger.info(f"Processing file: {json_file}")
                
                # 读取 JSON 文件
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 支持单个对象或数组
                if isinstance(data, dict):
                    data = [data]
                
                # 导入数据
                result = await self.import_from_json(
                    library_id=library_id,
                    json_data=data,
                    generate_embeddings=generate_embeddings
                )
                
                all_results["files_processed"] += 1
                all_results["total_patents"] += result["total"]
                all_results["success"] += result["success"]
                all_results["failed"] += result["failed"]
                all_results["errors"].extend(result["errors"])
                
            except Exception as e:
                error_msg = f"File {json_file}: {str(e)}"
                all_results["errors"].append(error_msg)
                logger.error(f"Failed to process file {json_file}", error=str(e))
        
        return all_results
    
    async def validate_import_data(
        self,
        json_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        验证导入数据格式
        
        Args:
            json_data: 待验证的数据
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        for idx, item in enumerate(json_data):
            row_num = idx + 1
            
            # 检查必需字段
            if not item.get("title"):
                errors.append(f"Row {row_num}: Missing required field 'title'")
            
            # 检查字段类型
            if item.get("claims") and not isinstance(item["claims"], (str, list)):
                errors.append(f"Row {row_num}: Field 'claims' should be string or list")
            
            if item.get("inventors") and not isinstance(item["inventors"], (str, list)):
                errors.append(f"Row {row_num}: Field 'inventors' should be string or list")
            
            # 警告
            if not item.get("abstract"):
                warnings.append(f"Row {row_num}: Missing 'abstract' field")
            
            if not item.get("application_no"):
                warnings.append(f"Row {row_num}: Missing 'application_no' field")
        
        return {
            "valid": len(errors) == 0,
            "total_rows": len(json_data),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings
        }


# 全局批量导入服务实例
batch_import_service = BatchImportService()
