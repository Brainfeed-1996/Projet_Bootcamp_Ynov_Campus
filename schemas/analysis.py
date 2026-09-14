from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    severity: str = Field(..., description="Niveau de sévérité (LOW, MEDIUM, HIGH, CRITICAL)")
    category: str = Field(..., description="Catégorie du log (ex: AUTH, NETWORK, SYSTEM)")
    summary: str = Field(..., description="Résumé de l'analyse")
    recommendations: list[str] = Field(..., description="Liste des recommandations")
    provider: str = Field(..., description="Fournisseur IA utilisé (openai, ollama, fake)")