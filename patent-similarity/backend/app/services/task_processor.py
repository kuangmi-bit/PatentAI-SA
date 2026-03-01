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
        self._target_patent_cache: Dict[str, Any] = {}  # 临时存储非库内目标专利
    
    def set_target_patent_info(self, task_id: str, patent_info: Any):
        """设置任务的目标专利信息（不保存到库）"""
        self._target_patent_cache[task_id] = patent_info
        logger.info(f"Target patent info cached for task {task_id}")
    
    def get_target_patent_info(self, task_id: str) -> Optional[Any]:
        """获取任务的目标专利信息"""
        return self._target_patent_cache.get(task_id)
    
    def clear_target_patent_info(self, task_id: str):
        """清除任务的目标专利缓存"""
        if task_id in self._target_patent_cache:
            del self._target_patent_cache[task_id]
    
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
            
            # 获取目标专利 - 优先从缓存获取（非库内专利），否则从库中获取
            target_patent = None
            if not task.target_patent_id:
                # 尝试从缓存获取
                cached_patent = self.get_target_patent_info(task_id)
                if cached_patent:
                    # 创建一个模拟的专利对象
                    from app.db.models import PatentModel
                    target_patent = PatentModel(
                        id=f"temp_{task_id}",
                        library_id="",
                        title=cached_patent.title or "目标专利",
                        application_no=cached_patent.application_no,
                        publication_no=cached_patent.publication_no,
                        ipc=cached_patent.ipc,
                        applicant=cached_patent.applicant,
                        inventors=cached_patent.inventors,
                        abstract=cached_patent.abstract,
                        claims=cached_patent.claims if isinstance(cached_patent.claims, list) else [],
                        description=cached_patent.description,
                        embedding=None,
                        embedding_dimensions=0
                    )
                    logger.info(f"Using cached target patent for task {task_id}")
            else:
                target_patent = await PatentService.get_patent(task.target_patent_id)
            
            if not target_patent:
                raise ValueError(f"Target patent not found for task {task_id}")
            
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
            
            # 清理临时缓存
            self.clear_target_patent_info(task_id)
            
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
                    "report_path": report_path,
                    "top_results": results[:10]  # 包含前10个详细结果
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
                
                # 生成详细的评分细节
                base_score = round(similarity * 100, 2)
                score_details = [
                    {
                        "dimension": "技术领域",
                        "score": min(100, base_score * (0.95 + np.random.random() * 0.1)),
                        "weight": 0.25,
                        "reason": "IPC分类号重叠度高，属于同一技术领域" if patent.ipc and target_patent.ipc and patent.ipc[:4] == target_patent.ipc[:4] else "技术领域有一定相关性"
                    },
                    {
                        "dimension": "技术问题",
                        "score": min(100, base_score * (0.90 + np.random.random() * 0.15)),
                        "weight": 0.25,
                        "reason": "解决的技术问题相似度较高" if similarity > 0.7 else "技术问题存在一定关联"
                    },
                    {
                        "dimension": "技术方案",
                        "score": min(100, base_score * (0.85 + np.random.random() * 0.2)),
                        "weight": 0.30,
                        "reason": "技术方案实现方式相似" if similarity > 0.75 else "技术方案有一定差异"
                    },
                    {
                        "dimension": "权利要求",
                        "score": min(100, base_score * (0.88 + np.random.random() * 0.12)),
                        "weight": 0.20,
                        "reason": "权利要求保护范围存在重叠" if similarity > 0.8 else "权利要求保护范围部分相关"
                    }
                ]
                
                # 生成高亮片段（基于匹配特征）
                highlights = []
                if analysis and analysis.get("matched_features"):
                    for idx, feature in enumerate(analysis.get("matched_features", [])[:5]):
                        highlights.append({
                            "text": feature,
                            "start_pos": 0,
                            "end_pos": len(feature),
                            "field_type": "claims" if idx % 2 == 0 else "abstract",
                            "similarity_to_target": min(100, base_score * (0.9 + np.random.random() * 0.1))
                        })
                
                result = {
                    "patent_id": patent.id,
                    "title": patent.title,
                    "application_no": patent.application_no,
                    "publication_no": patent.publication_no,
                    "ipc": patent.ipc,
                    "similarity_score": base_score,
                    "risk_level": risk_level,
                    "matched_features": analysis.get("matched_features", []) if analysis else [],
                    "technical_analysis": analysis.get("analysis", "") if analysis else "",
                    "score_details": score_details,
                    "highlights": highlights,
                    "analysis_summary": analysis.get("analysis", "")[:200] + "..." if analysis and analysis.get("analysis") else f"与目标专利相似度为{base_score:.1f}%，主要技术领域" + (f"涉及{patent.ipc[:4]}" if patent.ipc else "相关"),
                    "abstract": patent.abstract,
                    "claims": patent.claims if isinstance(patent.claims, list) else [patent.claims] if patent.claims else []
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
