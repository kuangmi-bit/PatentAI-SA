"""
Patent similarity analysis report generator
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from app.core.logging import get_logger
from app.models.schemas import RiskLevel

logger = get_logger(__name__)


class ReportGenerator:
    """分析报告生成器"""
    
    def __init__(self):
        self.reports_dir = Path("./reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_html_report(
        self,
        task_id: str,
        target_patent: Dict[str, Any],
        results: List[Dict[str, Any]],
        total_compared: int
    ) -> str:
        """
        生成 HTML 格式的分析报告
        
        Args:
            task_id: 任务ID
            target_patent: 目标专利信息
            results: 相似度分析结果
            total_compared: 对比专利总数
            
        Returns:
            HTML 报告内容
        """
        # 统计信息
        high_risk = len([r for r in results if r.get('risk_level') == RiskLevel.HIGH])
        medium_risk = len([r for r in results if r.get('risk_level') == RiskLevel.MEDIUM])
        low_risk = len([r for r in results if r.get('risk_level') == RiskLevel.LOW])
        
        avg_score = sum(r.get('similarity_score', 0) for r in results) / len(results) if results else 0
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>专利相似度分析报告 - {target_patent.get('title', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        h1 {{ color: #1a1a1a; margin-bottom: 10px; }}
        h2 {{ color: #333; margin: 30px 0 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #555; margin: 20px 0 10px; }}
        .meta {{ color: #666; font-size: 14px; margin-bottom: 30px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #1890ff;
        }}
        .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .risk-high {{ color: #ff4d4f; }}
        .risk-medium {{ color: #faad14; }}
        .risk-low {{ color: #52c41a; }}
        .patent-card {{
            border: 1px solid #e8e8e8;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            background: #fafafa;
        }}
        .patent-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .patent-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
        }}
        .similarity-score {{
            font-size: 24px;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            background: #e6f7ff;
            color: #1890ff;
        }}
        .patent-meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .features {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        .feature-tag {{
            background: #f0f0f0;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 13px;
            color: #555;
        }}
        .target-patent {{
            background: #e6f7ff;
            border: 1px solid #91d5ff;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 12px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>专利相似度分析报告</h1>
        <div class="meta">
            报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            任务ID: {task_id}
        </div>
        
        <div class="target-patent">
            <h3>目标专利</h3>
            <div class="patent-title">{target_patent.get('title', 'Unknown')}</div>
            <div class="patent-meta">
                申请号: {target_patent.get('application_no', 'N/A')} | 
                公开号: {target_patent.get('publication_no', 'N/A')} | 
                IPC: {target_patent.get('ipc', 'N/A')}
            </div>
            <div style="color: #666; margin-top: 10px;">
                {target_patent.get('abstract', '无摘要')[:200]}...
            </div>
        </div>
        
        <h2>分析概览</h2>
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{total_compared}</div>
                <div class="stat-label">对比专利总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(results)}</div>
                <div class="stat-label">相似专利数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_score:.1f}%</div>
                <div class="stat-label">平均相似度</div>
            </div>
            <div class="stat-card">
                <div class="stat-value risk-high">{high_risk}</div>
                <div class="stat-label">高风险专利</div>
            </div>
        </div>
        
        <h2>风险分布</h2>
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value risk-high">{high_risk}</div>
                <div class="stat-label">高风险 (≥85%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value risk-medium">{medium_risk}</div>
                <div class="stat-label">中风险 (70-85%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value risk-low">{low_risk}</div>
                <div class="stat-label">低风险 (&lt;70%)</div>
            </div>
        </div>
        
        <h2>相似专利详情 (Top {len(results)})</h2>
"""
        
        # 添加每个相似专利的详情
        for idx, result in enumerate(results, 1):
            risk_class = f"risk-{result.get('risk_level', 'low')}"
            features_html = ""
            if result.get('matched_features'):
                features_html = '<div class="features">' + ''.join([
                    f'<span class="feature-tag">{f}</span>'
                    for f in result['matched_features']
                ]) + '</div>'
            
            html += f"""
        <div class="patent-card">
            <div class="patent-header">
                <div>
                    <span style="color: #999; margin-right: 10px;">#{idx}</span>
                    <span class="patent-title">{result.get('title', 'Unknown')}</span>
                </div>
                <div class="similarity-score {risk_class}">{result.get('similarity_score', 0):.1f}%</div>
            </div>
            <div class="patent-meta">
                申请号: {result.get('application_no', 'N/A')} | 
                风险等级: <span class="{risk_class}">{result.get('risk_level', 'Unknown').upper()}</span>
            </div>
            {features_html}
        </div>
"""
        
        html += f"""
        <div class="footer">
            本报告由 PatentAI 系统自动生成 | 
            © {datetime.now().year} 金杜律师事务所
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_json_report(
        self,
        task_id: str,
        target_patent: Dict[str, Any],
        results: List[Dict[str, Any]],
        total_compared: int
    ) -> Dict[str, Any]:
        """生成 JSON 格式的报告"""
        return {
            "task_id": task_id,
            "generated_at": datetime.now().isoformat(),
            "target_patent": target_patent,
            "summary": {
                "total_compared": total_compared,
                "similar_patents_found": len(results),
                "high_risk_count": len([r for r in results if r.get('risk_level') == RiskLevel.HIGH]),
                "medium_risk_count": len([r for r in results if r.get('risk_level') == RiskLevel.MEDIUM]),
                "low_risk_count": len([r for r in results if r.get('risk_level') == RiskLevel.LOW]),
            },
            "results": results
        }
    
    async def save_report(
        self,
        task_id: str,
        report_data: Dict[str, Any],
        format: str = "html"
    ) -> str:
        """
        保存报告到文件
        
        Args:
            task_id: 任务ID
            report_data: 报告数据
            format: 报告格式 (html/json)
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{task_id}_{timestamp}.{format}"
        filepath = self.reports_dir / filename
        
        if format == "html":
            content = self.generate_html_report(
                task_id=task_id,
                target_patent=report_data["target_patent"],
                results=report_data["results"],
                total_compared=report_data["total_compared"]
            )
            filepath.write_text(content, encoding="utf-8")
        else:
            filepath.write_text(
                json.dumps(report_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        
        logger.info(f"Report saved: {filepath}")
        return str(filepath)


# 全局报告生成器实例
report_generator = ReportGenerator()
