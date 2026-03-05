"""
Geometric Engine – Enterprise HVAC AI System v1.0.0
SMACNA-compliant fitting geometry engine (units: inches).
"""

from geometric_engine.models import (
    FittingType,
    ConnectionType,
    InsulationType,
    PressureClass,
    FittingParameters,
    ValidationReport,
    FittingResult,
)
from geometric_engine.ai_module import VisionAIModelGenerator
from geometric_engine.parametric_module import ManualParametricInputSystem
from geometric_engine.wizard_module import SMACNAGuidedWizard
from geometric_engine.training import TrainingExample, TrainingCorpus, ModelTrainer

__version__ = "1.0.0"
__all__ = [
    "FittingType",
    "ConnectionType",
    "InsulationType",
    "PressureClass",
    "FittingParameters",
    "ValidationReport",
    "FittingResult",
    "VisionAIModelGenerator",
    "ManualParametricInputSystem",
    "SMACNAGuidedWizard",
    "TrainingExample",
    "TrainingCorpus",
    "ModelTrainer",
]
