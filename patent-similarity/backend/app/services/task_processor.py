"""
Asynchronous task processor for patent similarity analysis
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

from app.core.logging import get_logger
from app.core.config import settings
from app.services.db_service import TaskService, PatentService, ResultService, LibraryService
from app.services.zhipu_client import ZhipuClient, PatentEmbedder
from app.services.vector_store import VectorStore
from app.services.report_generator import report_generator
from app.models.schemas import TaskStatus, RiskLevel

logger = get_logger(__name__)


class TaskProcessor:
    """异步任务处理器"""
    
    def __init__(self):
        self.zhipu_client = ZhipuClient()
        self.embedder = PatentEmbedder(self.zhipu_client)
        self.vector_store = VectorStore()
        self._running_tasks: Dict[str, asyncio.Task] = {}
    
    async def submit_task(self, task_id: str) -> bool:
        """提交任务进行异步处理"""
        if task_id in self._running_tasks:
            logger.warning(f"Task {task_id} is already running")
            return False
        
        # 创建异步任务
        async_task = asyncio.create_task(self._process_task(task_id))
        self._running_tasks[task_id] = async_task
        
        # 添加完成回调
        async_task.add_done_callback(lambda t: self._running_tasks.pop(task_id, None))
        
        logger.info(f"Task {task_id} submitted for processing")
        return True
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消正在运行的任务"""
        if task_id not in self._running_tasks:
            return False
        
        async_task = self._running_tasks[task_id]
        async_task.cancel()
        
        try:
            await async_task
        except asyncio.CancelledError:
            pass
        
        logger.info(f"Task {task_id} cancelled")
        return True
    
    async def _process_task(self, task_id: str):
        """处理分析任务的主流程"""
        try:
            # 获取任务信息
            task = await TaskService.get_task(task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return
            
            # 更新状态为运行中
            await TaskService.update_task_status(
                task_id=task_id,
                status="running",
                progress=10
            )
            
            # 获取目标专利
            target_patent = await PatentService.get_patent(task.target_patent_id)
            if not target_patent:
                raise ValueError(f"Target patent {task.target_patent_id} not found")
            
            # 获取对比库中的所有专利
            comparison_patents = await PatentService.list_patents(
                library_id=task.library_id,
                limit=1000
            )
            
            if not comparison_patents:
                raise ValueError(f"No patents found in library {task.library_id}")
            
            logger.info(
                f"Processing task {task_id}",
                target_patent=target_patent.id,
                comparison_count=len(comparison_patents)
            )
            
            # 更新进度
            await TaskService.update_task_status(
                task_id=task_id,
                status="running",
                progress=30
            )
            
            # 生成目标专利的嵌入向量
            target_embedding = await self._get_or_create_embedding(target_patent)
            
            # 更新进度
            await TaskService.update_task_status(
                task_id=task_id,
                status="running",
                progress=50
            )
            
            # 执行相似度分析
            results = await self._analyze_similarity(
                target_patent=target_patent,
                target_embedding=target_embedding,
                comparison_patents=comparison_patents,
                task_id=task_id
            )
            
            # 更新进度
            await TaskService.update_task_status(
                task_id=task_id,
                status="running",
                progress=90
            )
            
            # 保存结果
            await self._save_results(task_id, target_patent.id, results)
            
            # 生成报告
            try:
                target_patent_dict = {
                    "title": target_patent.title,
                    "application_no": target_patent.application_no,
                    "publication_no": target_patent.publication_no,
                    "ipc": target_patent.ipc,
                    "abstract": target_patent.abstract
                }
                
                report_path = await report_generator.save_report(
                    task_id=task_id,
                    report_data={
                        "target_patent": target_patent_dict,
                        "results": results,
                        "total_compared": len(comparison_patents)
                    },
                    format="html"
                )
                logger.info(f"Report generated: {report_path}")
            except Exception as e:
                logger.error(f"Failed to generate report: {str(e)}")
                report_path = None
            
            # 标记任务完成
            await TaskService.update_task_status(
                task_id=task_id,
                status="completed",
                progress=100,
                result={
                    "top_matches": len(results),
                    "total_compared": len(comparison_patents),
                    "highest_score": results[0]["similarity_score"] if results else 0,
                    "report_path": report_path
                }
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except asyncio.CancelledError:
            logger.info(f"Task {task_id} was cancelled")
            await TaskService.update_task_status(
                task_id=task_id,
                status="cancelled",
                progress=0
            )
            raise
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            await TaskService.update_task_status(
                task_id=task_id,
                status="failed",
                progress=0,
                error_message=str(e)
            )
    
    async def _get_or_create_embedding(self, patent) -> List[float]:
        """获取或创建专利的嵌入向量"""
        # 如果已有嵌入向量，直接返回
        if patent.embedding and patent.embedding_dimensions > 0:
            return patent.embedding
        
        # 生成嵌入向量
        patent_text = self._format_patent_for_embedding(patent)
        embedding = await self.embedder.embed_text(patent_text)
        
        # 保存到数据库
        await PatentService.update_embedding(
            patent_id=patent.id,
            embedding=embedding,
            dimensions=len(embedding)
        )
        
        return embedding
    
    def _format_patent_for_embedding(self, patent) -> str:
        """格式化专利文本用于嵌入"""
        parts = []
        
        if patent.title:
            parts.append(f"标题: {patent.title}")
        
        if patent.abstract:
            parts.append(f"摘要: {patent.abstract}")
        
        if patent.claims:
            if isinstance(patent.claims, list):
                parts.append(f"权利要求: {' '.join(patent.claims)}")
            else:
                parts.append(f"权利要求: {patent.claims}")
        
        if patent.description:
            parts.append(f"说明书: {patent.description[:2000]}")  # 限制长度
        
        return "\n".join(parts)
    
    async def _analyze_similarity(
        self,
        target_patent,
        target_embedding: List[float],
        comparison_patents: List[Any],
        task_id: str
    ) -> List[Dict[str, Any]]:
        """分析相似度"""
        results = []
        total = len(comparison_patents)
        
        for idx, patent in enumerate(comparison_patents):
            # 跳过自己对比自己
            if patent.id == target_patent.id:
                continue
            
            try:
                # 获取或创建对比专利的嵌入
                comparison_embedding = await self._get_or_create_embedding(patent)
                
                # 计算余弦相似度
                similarity = self._cosine_similarity(target_embedding, comparison_embedding)
                
                # 确定风险等级
                risk_level = self._determine_risk_level(similarity)
                
                # 使用 LLM 进行详细分析（对于高相似度专利）
                analysis = None
                if similarity > 0.7:
                    analysis = await self._detailed_analysis(target_patent, patent)
                
                result = {
                    "patent_id": patent.id,
                    "title": patent.title,
                    "application_no": patent.application_no,
                    "publication_no": patent.publication_no,
                    "similarity_score": round(similarity * 100, 2),
                    "risk_level": risk_level,
                    "matched_features": analysis.get("matched_features", []) if analysis else [],
                    "technical_analysis": analysis.get("analysis", "") if analysis else ""
                }
                results.append(result)
                
                # 每10个专利更新一次进度
                if idx % 10 == 0:
                    progress = 50 + int((idx / total) * 40)
                    await TaskService.update_task_status(
                        task_id=task_id,
                        status="running",
                        progress=min(progress, 89)
                    )
                
            except Exception as e:
                logger.error(f"Error analyzing patent {patent.id}: {str(e)}")
                continue
        
        # 按相似度排序
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results[:20]  # 返回前20个最相似的结果
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        a = np.array(vec1)
        b = np.array(vec2)
        
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _determine_risk_level(self, similarity: float) -> str:
        """根据相似度确定风险等级"""
        if similarity >= 0.85:
            return RiskLevel.HIGH
        elif similarity >= 0.70:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _detailed_analysis(self, target_patent, comparison_patent) -> Dict[str, Any]:
        """使用 LLM 进行详细相似度分析"""
        try:
            # Format patents as text for analysis
            target_text = self._format_patent_for_embedding(target_patent)
            comparison_text = self._format_patent_for_embedding(comparison_patent)
            
            analysis = await self.zhipu_client.analyze_patent_similarity(
                target_text,
                comparison_text
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Detailed analysis failed: {str(e)}")
            return {"matched_features": [], "analysis": ""}
    
    async def _save_results(
        self,
        task_id: str,
        target_patent_id: str,
        results: List[Dict[str, Any]]
    ):
        """保存分析结果到数据库"""
        for idx, result in enumerate(results):
            await ResultService.create_result(
                task_id=task_id,
                target_patent_id=target_patent_id,
                comparison_patent_id=result["patent_id"],
                similarity_score=result["similarity_score"],
                risk_level=result["risk_level"],
                matched_features=result.get("matched_features", [])
            )
        
        logger.info(f"Saved {len(results)} results for task {task_id}")


# 全局任务处理器实例
task_processor = TaskProcessor()
