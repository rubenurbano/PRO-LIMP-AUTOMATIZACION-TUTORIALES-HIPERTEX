"""
Report generator for daily opportunity reports.
"""
from typing import List, Dict, Any
import json
from datetime import datetime, date
from pathlib import Path
import logging
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Opportunity, DailyReport

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generator for daily opportunity reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.reports_dir = Path(settings.reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_daily_report(
        self,
        opportunities: List[Opportunity],
        metadata: Dict[str, Any]
    ) -> DailyReport:
        """
        Generate a daily report from opportunities.
        
        Args:
            opportunities: List of top 10 opportunities
            metadata: Execution metadata (sources consulted, time, etc.)
            
        Returns:
            DailyReport object
        """
        report_date = date.today()
        
        # Generate JSON report
        report_json = self._generate_json_report(opportunities, metadata, report_date)
        
        # Generate HTML email
        report_html = self._generate_html_report(opportunities, metadata, report_date)
        
        # Save to database
        daily_report = DailyReport(
            report_date=report_date,
            top_opportunities=[opp.id for opp in opportunities],
            report_json=report_json,
            report_html=report_html,
            sources_consulted=metadata.get("sources_consulted", 0),
            total_analyzed=metadata.get("total_analyzed", 0),
            execution_time_minutes=metadata.get("execution_time_minutes", 0)
        )
        
        self.db.add(daily_report)
        self.db.commit()
        
        # Save JSON to file
        json_path = self.reports_dir / f"report_{report_date.isoformat()}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated daily report for {report_date}")
        
        return daily_report
    
    def _generate_json_report(
        self,
        opportunities: List[Opportunity],
        metadata: Dict[str, Any],
        report_date: date
    ) -> Dict[str, Any]:
        """Generate structured JSON report."""
        return {
            "fecha": report_date.isoformat(),
            "version": "1.0",
            "oportunidades": [
                self._opportunity_to_dict(opp, rank + 1)
                for rank, opp in enumerate(opportunities)
            ],
            "metadata": {
                "fuentes_consultadas": metadata.get("sources_consulted", 0),
                "total_problemas_analizados": metadata.get("total_analyzed", 0),
                "tiempo_ejecucion_minutos": round(metadata.get("execution_time_minutes", 0), 2),
                "modelo_usado": settings.gemini_model
            }
        }
    
    def _opportunity_to_dict(self, opp: Opportunity, ranking: int) -> Dict[str, Any]:
        """Convert Opportunity model to dictionary for report."""
        return {
            "id": opp.public_id,
            "ranking": ranking,
            "titulo": opp.title,
            "descripcion_problema": opp.problem_description,
            "sector": opp.sector or "Unknown",
            "tipo_solucion": opp.solution_type or "Unknown",
            "propuesta_app": opp.proposed_app or {},
            "usuarios_ideales": opp.ideal_users or {},
            "beneficio_economico": opp.economic_benefit or {},
            "puntuacion": {
                "total": float(opp.score_total) if opp.score_total else 0.0,
                "desglose": opp.score_breakdown or {}
            },
            "tags": opp.tags or [],
            "fecha_creacion": opp.created_at.isoformat() if opp.created_at else None
        }
    
    def _generate_html_report(
        self,
        opportunities: List[Opportunity],
        metadata: Dict[str, Any],
        report_date: date
    ) -> str:
        """Generate HTML email report."""
        opportunities_html = "\n".join([
            self._opportunity_to_html(opp, rank + 1)
            for rank, opp in enumerate(opportunities)
        ])
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .opportunity {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .opportunity h2 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 20px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 8px;
        }}
        .badge-score {{
            background: #ffd700;
            color: #333;
        }}
        .badge-sector {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        .description {{
            margin: 15px 0;
            color: #555;
        }}
        .features {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
        }}
        .features h4 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 14px;
        }}
        .features ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Daily Business Opportunities</h1>
        <p>{report_date.strftime('%d de %B, %Y')}</p>
        <p>📊 {metadata.get('total_analyzed', 0)} oportunidades analizadas | 
           ⏱️ {round(metadata.get('execution_time_minutes', 0), 1)} minutos de ejecución</p>
    </div>
    
    {opportunities_html}
    
    <div class="footer">
        <p>Business Opportunities Finder v1.0</p>
        <p>Powered by Gemini {settings.gemini_model}</p>
    </div>
</body>
</html>
"""
    
    def _opportunity_to_html(self, opp: Opportunity, ranking: int) -> str:
        """Convert opportunity to HTML card."""
        score = float(opp.score_total) if opp.score_total else 0.0
        proposed_app = opp.proposed_app or {}
        features = proposed_app.get("key_features", [])
        
        features_html = ""
        if features:
            features_list = "".join([f"<li>{feature}</li>" for feature in features[:5]])
            features_html = f"""
            <div class="features">
                <h4>💡 Features Clave:</h4>
                <ul>{features_list}</ul>
            </div>
            """
        
        return f"""
    <div class="opportunity">
        <div>
            <span class="badge badge-score">⭐ {score:.1f}/10</span>
            <span class="badge badge-sector">{opp.sector or 'Unknown'}</span>
        </div>
        <h2>#{ranking} - {opp.title}</h2>
        <div class="description">
            {opp.problem_description[:300]}{'...' if len(opp.problem_description) > 300 else ''}
        </div>
        {features_html}
        <p><strong>Solución propuesta:</strong> {proposed_app.get('name', 'N/A')}</p>
        <p><strong>MVP estimado:</strong> {proposed_app.get('mvp_estimate', 'N/A')}</p>
        <p><strong>Pricing:</strong> {proposed_app.get('pricing_model', 'N/A')}</p>
    </div>
"""
