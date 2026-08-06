"""Small deterministic bilingual fixtures for local development and tests."""

from dataclasses import dataclass

from bridge_surface.translation.contracts import PreservationReason, PreservedTerm


@dataclass(frozen=True, slots=True)
class BilingualFixture:
    """One approved Japanese/English pair used by the mock provider."""

    fixture_id: str
    english_text: str
    japanese_text: str
    preserved_terms: tuple[PreservedTerm, ...]


FIXTURES: tuple[BilingualFixture, ...] = (
    BilingualFixture(
        fixture_id="inspection-identifiers",
        english_text=("Please inspect EQ-1048 and WO123456 against Drawing 22A-118 at 0.05 mm."),
        japanese_text=("EQ-1048とWO123456をDrawing 22A-118の0.05 mm基準で検査してください。"),
        preserved_terms=(
            PreservedTerm(term="EQ-1048", reason=PreservationReason.IDENTIFIER),
            PreservedTerm(term="WO123456", reason=PreservationReason.IDENTIFIER),
            PreservedTerm(term="Drawing 22A-118", reason=PreservationReason.IDENTIFIER),
            PreservedTerm(term="0.05 mm", reason=PreservationReason.NUMERIC_VALUE),
        ),
    ),
    BilingualFixture(
        fixture_id="repair-before-trial",
        english_text=("Robot 17 downtime requires a permanent repair before the production trial."),
        japanese_text="Robot 17の停止時間に対応するため、トライ生産前に恒久修理が必要です。",
        preserved_terms=(PreservedTerm(term="Robot 17", reason=PreservationReason.IDENTIFIER),),
    ),
)
