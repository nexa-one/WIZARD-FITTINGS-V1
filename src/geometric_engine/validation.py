"""
Validation module – dimension, geometry, and fabrication checks.

All checks populate a :class:`~geometric_engine.models.ValidationReport`.
"""

from __future__ import annotations

from geometric_engine.models import (
    FittingParameters,
    FittingType,
    ValidationReport,
)


def check_invalid_geometry(
    params: FittingParameters, report: ValidationReport
) -> None:
    """Detect geometrically impossible configurations."""
    ft = params.fitting_type

    # Elbows must have angle set
    if ft in (FittingType.ELBOW_90, FittingType.ELBOW_45):
        expected = 90.0 if ft == FittingType.ELBOW_90 else 45.0
        if params.angle is not None and params.angle != expected:
            report.add_error(
                f"{ft.value} elbow angle must be {expected}°, got {params.angle}°."
            )
            report.geometry_valid = False

    # Transition: ensure output width is different from input width
    if ft == FittingType.TRANSITION:
        if (
            params.neck_out is not None
            and abs(params.neck_out - params.width) < 1e-9
            and abs(params.height - params.height) < 1e-9
        ):
            report.add_warning(
                "Transition with identical inlet and outlet dimensions is effectively "
                "a straight section."
            )

    # Elbow radius must be positive
    if ft in (FittingType.ELBOW_90, FittingType.ELBOW_45):
        from geometric_engine.smacna import elbow_radius

        r = elbow_radius(params.width)
        if r <= 0:
            report.add_error("Elbow radius must be positive.")
            report.geometry_valid = False

    # Length must be positive when provided
    if params.length is not None and params.length <= 0:
        report.add_error(f"Length must be positive, got {params.length}.")
        report.geometry_valid = False


def check_fabrication_constraints(
    params: FittingParameters, report: ValidationReport
) -> None:
    """Check practical sheet-metal fabrication limits."""
    # Minimum duct dimension: 2 inches (smallest practical duct)
    min_dim = 2.0
    if params.width < min_dim:
        report.add_error(
            f"Width {params.width}\" is below fabrication minimum of {min_dim}\"."
        )
        report.fabrication_feasible = False
    if params.height < min_dim:
        report.add_error(
            f"Height {params.height}\" is below fabrication minimum of {min_dim}\"."
        )
        report.fabrication_feasible = False

    # Aspect ratio check: SMACNA recommends ≤ 4:1 for best performance
    if params.width > 0 and params.height > 0:
        ratio = max(params.width, params.height) / min(params.width, params.height)
        if ratio > 8.0:
            report.add_warning(
                f"Aspect ratio {ratio:.1f}:1 exceeds practical 8:1 fabrication limit."
            )

    # Neck lengths must be positive when set
    for name, val in (("neck_in", params.neck_in), ("neck_out", params.neck_out)):
        if val is not None and val <= 0:
            report.add_error(f"{name} must be positive, got {val}.")
            report.fabrication_feasible = False


def check_no_negative_dimensions(
    params: FittingParameters, report: ValidationReport
) -> None:
    """Reject any negative or zero primary dimension."""
    for name, val in (
        ("width", params.width),
        ("height", params.height),
    ):
        if val <= 0:
            report.add_error(f"{name} must be > 0, got {val}.")
            report.is_valid = False
            report.geometry_valid = False


def validate(
    params: FittingParameters,
    *,
    smacna_enforcement: bool = True,
) -> ValidationReport:
    """
    Run the full validation pipeline for *params*.

    Parameters
    ----------
    params:
        Fitting parameters to validate (defaults should already be applied).
    smacna_enforcement:
        When True, also run SMACNA-specific checks.

    Returns
    -------
    ValidationReport
        Populated report; ``report.is_valid`` is False when any error was found.
    """
    report = ValidationReport()

    check_no_negative_dimensions(params, report)
    check_invalid_geometry(params, report)
    check_fabrication_constraints(params, report)

    if smacna_enforcement:
        from geometric_engine.smacna import check_smacna_compliance

        check_smacna_compliance(params, report)

    return report
