"""
Database service layer for patent operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import joinedload

from app.db.database import get_db
from app.db.models import LibraryModel, PatentModel, TaskModel, SimilarityResultModel
from app.core.logging import get_logger

logger = get_logger(__name__)


class LibraryService:
    """专利库服务"""
    
    @staticmethod
    async def create_library(name: str, description: str = None) -> LibraryModel:
        """创建专利库"""
        async with get_db() as session:
            library = LibraryModel(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                patent_count=0,
                size_mb=0.0
            )
            session.add(library)
            await session.commit()
            await session.refresh(library)
            logger.info(f"Library created: {library.id} - {name}")
            return library
    
    @staticmethod
    async def get_library(library_id: str) -> Optional[LibraryModel]:
        """获取专利库详情"""
        async with get_db() as session:
            result = await session.execute(
                select(LibraryModel)
                .where(LibraryModel.id == library_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def list_libraries(skip: int = 0, limit: int = 100) -> List[LibraryModel]:
        """列出所有专利库"""
        async with get_db() as session:
            result = await session.execute(
                select(LibraryModel)
                .order_by(LibraryModel.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
    
    @staticmethod
    async def update_library(library_id: str, **kwargs) -> Optional[LibraryModel]:
        """更新专利库信息"""
        async with get_db() as session:
            await session.execute(
                update(LibraryModel)
                .where(LibraryModel.id == library_id)
                .values(updated_at=datetime.utcnow(), **kwargs)
            )
            await session.commit()
            return await LibraryService.get_library(library_id)
    
    @staticmethod
    async def delete_library(library_id: str) -> bool:
        """删除专利库"""
        async with get_db() as session:
            result = await session.execute(
                delete(LibraryModel).where(LibraryModel.id == library_id)
            )
            await session.commit()
            return result.rowcount > 0
    
    @staticmethod
    async def update_patent_count(library_id: str) -> int:
        """更新专利数量"""
        async with get_db() as session:
            count_result = await session.execute(
                select(func.count(PatentModel.id))
                .where(PatentModel.library_id == library_id)
            )
            count = count_result.scalar()
            
            await session.execute(
                update(LibraryModel)
                .where(LibraryModel.id == library_id)
                .values(patent_count=count, updated_at=datetime.utcnow())
            )
            await session.commit()
            return count


class PatentService:
    """专利文档服务"""
    
    @staticmethod
    async def create_patent(
        library_id: str,
        title: str,
        application_no: str = None,
        publication_no: str = None,
        ipc: str = None,
        applicant: str = None,
        inventors: str = None,
        abstract: str = None,
        claims: str = None,
        description: str = None,
        file_path: str = None,
        file_name: str = None,
        embedding: list = None,
        embedding_dimensions: int = 0,
        quality_score: int = None
    ) -> PatentModel:
        """创建专利文档"""
        async with get_db() as session:
            # Parse inventors from string to list if needed
            inventors_list = None
            if inventors:
                inventors_list = [i.strip() for i in inventors.split(",") if i.strip()]
            
            # Parse claims from string to list if needed
            claims_list = None
            if claims:
                claims_list = [c.strip() for c in claims.split("\n\n") if c.strip()]
            
            patent = PatentModel(
                id=str(uuid.uuid4()),
                library_id=library_id,
                title=title,
                application_no=application_no,
                publication_no=publication_no,
                ipc=ipc,
                applicant=applicant,
                inventors=inventors_list,
                abstract=abstract,
                claims=claims_list,
                description=description,
                file_path=file_path,
                file_name=file_name,
                embedding=embedding,
                embedding_dimensions=embedding_dimensions,
                extraction_quality=quality_score or 0
            )
            session.add(patent)
            await session.commit()
            await session.refresh(patent)
            
            # 更新专利库数量
            await LibraryService.update_patent_count(library_id)
            
            logger.info(f"Patent created: {patent.id} - {title[:50]}...")
            return patent
    
    @staticmethod
    async def get_patent(patent_id: str) -> Optional[PatentModel]:
        """获取专利详情"""
        async with get_db() as session:
            result = await session.execute(
                select(PatentModel).where(PatentModel.id == patent_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def list_patents(
        library_id: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PatentModel]:
        """列出专利文档"""
        async with get_db() as session:
            query = select(PatentModel).order_by(PatentModel.created_at.desc())
            if library_id:
                query = query.where(PatentModel.library_id == library_id)
            result = await session.execute(query.offset(skip).limit(limit))
            return result.scalars().all()
    
    @staticmethod
    async def update_patent(patent_id: str, **kwargs) -> Optional[PatentModel]:
        """更新专利信息"""
        async with get_db() as session:
            await session.execute(
                update(PatentModel)
                .where(PatentModel.id == patent_id)
                .values(updated_at=datetime.utcnow(), **kwargs)
            )
            await session.commit()
            return await PatentService.get_patent(patent_id)
    
    @staticmethod
    async def delete_patent(patent_id: str) -> bool:
        """删除专利文档"""
        async with get_db() as session:
            # 获取专利信息以更新库数量
            patent = await PatentService.get_patent(patent_id)
            if not patent:
                return False
            
            library_id = patent.library_id
            
            result = await session.execute(
                delete(PatentModel).where(PatentModel.id == patent_id)
            )
            await session.commit()
            
            # 更新专利库数量
            if result.rowcount > 0:
                await LibraryService.update_patent_count(library_id)
            
            return result.rowcount > 0
    
    @staticmethod
    async def search_patents(
        keyword: str,
        library_id: str = None,
        limit: int = 20
    ) -> List[PatentModel]:
        """搜索专利（标题、摘要、申请人）"""
        async with get_db() as session:
            query = select(PatentModel).where(
                (PatentModel.title.ilike(f"%{keyword}%")) |
                (PatentModel.abstract.ilike(f"%{keyword}%")) |
                (PatentModel.applicant.ilike(f"%{keyword}%"))
            )
            if library_id:
                query = query.where(PatentModel.library_id == library_id)
            
            result = await session.execute(query.limit(limit))
            return result.scalars().all()
    
    @staticmethod
    async def update_embedding(
        patent_id: str,
        embedding: List[float],
        dimensions: int
    ) -> bool:
        """更新专利嵌入向量"""
        async with get_db() as session:
            result = await session.execute(
                update(PatentModel)
                .where(PatentModel.id == patent_id)
                .values(
                    embedding=embedding,
                    embedding_dimensions=dimensions,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
            return result.rowcount > 0


class TaskService:
    """分析任务服务"""
    
    @staticmethod
    async def create_task(
        name: str,
        library_id: str,
        target_patent_id: str = None,
        owner_id: str = None
    ) -> TaskModel:
        """创建分析任务"""
        async with get_db() as session:
            task = TaskModel(
                id=str(uuid.uuid4()),
                name=name,
                library_id=library_id,
                target_patent_id=target_patent_id,
                owner_id=owner_id,
                status="pending",
                progress=0
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            logger.info(f"Task created: {task.id} - {name}")
            return task
    
    @staticmethod
    async def get_task(task_id: str) -> Optional[TaskModel]:
        """获取任务详情"""
        async with get_db() as session:
            result = await session.execute(
                select(TaskModel).where(TaskModel.id == task_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def list_tasks(
        status: str = None,
        library_id: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskModel]:
        """列出分析任务"""
        async with get_db() as session:
            query = select(TaskModel).order_by(TaskModel.created_at.desc())
            if status:
                query = query.where(TaskModel.status == status)
            if library_id:
                query = query.where(TaskModel.library_id == library_id)
            result = await session.execute(query.offset(skip).limit(limit))
            return result.scalars().all()
    
    @staticmethod
    async def update_task_status(
        task_id: str,
        status: str,
        progress: int = None,
        error_message: str = None,
        result: dict = None
    ) -> Optional[TaskModel]:
        """更新任务状态"""
        async with get_db() as session:
            update_values = {"status": status}
            if progress is not None:
                update_values["progress"] = progress
            if error_message:
                update_values["error_message"] = error_message
            if result:
                update_values["result"] = result
            
            if status == "completed":
                update_values["completed_at"] = datetime.utcnow()
            
            await session.execute(
                update(TaskModel)
                .where(TaskModel.id == task_id)
                .values(updated_at=datetime.utcnow(), **update_values)
            )
            await session.commit()
            return await TaskService.get_task(task_id)
    
    @staticmethod
    async def delete_task(task_id: str) -> bool:
        """删除任务"""
        async with get_db() as session:
            result = await session.execute(
                delete(TaskModel).where(TaskModel.id == task_id)
            )
            await session.commit()
            return result.rowcount > 0


class ResultService:
    """相似度结果服务"""
    
    @staticmethod
    async def create_result(
        task_id: str,
        target_patent_id: str,
        comparison_patent_id: str,
        similarity_score: float,
        risk_level: str,
        technical_field_score: float = None,
        technical_problem_score: float = None,
        technical_solution_score: float = None,
        matched_features: List[str] = None,
        analysis: str = None
    ) -> SimilarityResultModel:
        """创建相似度分析结果"""
        async with get_db() as session:
            result = SimilarityResultModel(
                id=str(uuid.uuid4()),
                task_id=task_id,
                target_patent_id=target_patent_id,
                comparison_patent_id=comparison_patent_id,
                similarity_score=similarity_score,
                risk_level=risk_level,
                technical_field_score=technical_field_score,
                technical_problem_score=technical_problem_score,
                technical_solution_score=technical_solution_score,
                matched_features=matched_features or [],
                analysis=analysis
            )
            session.add(result)
            await session.commit()
            await session.refresh(result)
            logger.info(f"Result created for task: {task_id}")
            return result
    
    @staticmethod
    async def get_result(result_id: str) -> Optional[SimilarityResultModel]:
        """获取结果详情"""
        async with get_db() as session:
            result = await session.execute(
                select(SimilarityResultModel).where(SimilarityResultModel.id == result_id)
            )
            return result.scalar_one_or_none()
    
    @staticmethod
    async def list_results_by_task(task_id: str, limit: int = 100) -> List[SimilarityResultModel]:
        """通过任务ID获取结果列表"""
        async with get_db() as session:
            result = await session.execute(
                select(SimilarityResultModel)
                .where(SimilarityResultModel.task_id == task_id)
                .order_by(SimilarityResultModel.similarity_score.desc())
                .limit(limit)
            )
            return result.scalars().all()
