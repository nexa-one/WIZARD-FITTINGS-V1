"""
Training Module – AI Model Trainer
====================================
Answers the question: *¿Cómo entrenamos nuestra IA?*
                      *How do we train our AI?*

The ``VisionAIModelGenerator`` uses deterministic keyword-matching rules to
parse natural-language descriptions and image-metadata dicts.  This module
adds a **feedback-driven training loop** that lets operators:

1. Record labeled corrections (a description or image-metadata dict plus the
   known-correct answers).
2. Persist those corrections as a :class:`TrainingCorpus` (plain JSON, no
   external dependencies).
3. Train a :class:`ModelTrainer` on the corpus to derive new keyword →
   FittingType / ConnectionType / InsulationType / PressureClass mappings.
4. Pass the learned mappings back into :class:`~geometric_engine.ai_module.
   VisionAIModelGenerator` so that future predictions benefit from the
   corrections.

No ML runtime is required – the "training" is *frequency-based keyword
induction*: if a particular word appears in descriptions that were corrected
to fitting_type=``elbow_90``, and that word is not already in the built-in
keyword map, it gets added with a confidence that scales with how often it
appears alongside that label.

Typical workflow
----------------
>>> from geometric_engine.training import TrainingCorpus, ModelTrainer
>>> from geometric_engine.ai_module import VisionAIModelGenerator
>>>
>>> # 1.  Create / load a corpus
>>> corpus = TrainingCorpus()
>>>
>>> # 2.  Record corrections from real usage
>>> corpus.add_example(
...     input_text="codo 90 grados 24x12 TDC",
...     correct_fitting_type="elbow_90",
...     correct_connection_type="tdc",
...     notes="Spanish-language input",
... )
>>>
>>> # 3.  Train
>>> trainer = ModelTrainer()
>>> trainer.fit(corpus)
>>>
>>> # 4.  Use the updated AI
>>> ai = VisionAIModelGenerator(learned_keywords=trainer.learned_keywords)
>>> result = ai.process_natural_language("codo 90 24x12")
>>> assert result["fitting_type"] == "elbow_90"
>>>
>>> # 5.  Persist the corpus for next session
>>> corpus.save("my_corpus.json")
>>> corpus2 = TrainingCorpus.load("my_corpus.json")
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from geometric_engine.models import (
    ConnectionType,
    FittingType,
    InsulationType,
    PressureClass,
)


# ---------------------------------------------------------------------------
# TrainingExample
# ---------------------------------------------------------------------------


@dataclass
class TrainingExample:
    """
    A single labeled training example.

    At least one of *input_text* or *image_metadata* must be provided.
    At least *correct_fitting_type* must be given; other labels are optional.
    """

    correct_fitting_type: str  # FittingType value string, e.g. "elbow_90"
    input_text: Optional[str] = None
    image_metadata: Optional[Dict[str, Any]] = None
    correct_connection_type: Optional[str] = None   # ConnectionType value
    correct_pressure_class: Optional[str] = None    # PressureClass value
    correct_insulation_type: Optional[str] = None   # InsulationType value
    notes: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if self.input_text is None and self.image_metadata is None:
            raise ValueError(
                "TrainingExample requires at least one of input_text or image_metadata."
            )
        # Validate enum values
        FittingType(self.correct_fitting_type)
        if self.correct_connection_type is not None:
            ConnectionType(self.correct_connection_type)
        if self.correct_pressure_class is not None:
            PressureClass(self.correct_pressure_class)
        if self.correct_insulation_type is not None:
            InsulationType(self.correct_insulation_type)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TrainingExample:
        return cls(**data)


# ---------------------------------------------------------------------------
# TrainingCorpus
# ---------------------------------------------------------------------------


class TrainingCorpus:
    """
    An ordered collection of :class:`TrainingExample` instances.

    Examples can be added programmatically (via :meth:`add_example` or
    :meth:`add`), persisted to a JSON file (:meth:`save`), and reloaded
    (:meth:`load`).

    Parameters
    ----------
    name:
        Optional human-readable name for the corpus (stored in the JSON).
    """

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._examples: List[TrainingExample] = []

    # ------------------------------------------------------------------
    # Adding examples
    # ------------------------------------------------------------------

    def add_example(
        self,
        *,
        correct_fitting_type: str,
        input_text: Optional[str] = None,
        image_metadata: Optional[Dict[str, Any]] = None,
        correct_connection_type: Optional[str] = None,
        correct_pressure_class: Optional[str] = None,
        correct_insulation_type: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> TrainingExample:
        """
        Construct and register a new :class:`TrainingExample`.

        Parameters
        ----------
        correct_fitting_type:
            The ground-truth fitting type string (e.g. ``"elbow_90"``).
        input_text:
            Natural-language description used as the AI input.
        image_metadata:
            Image-metadata dict used as the AI input.
        correct_connection_type, correct_pressure_class, correct_insulation_type:
            Optional extra ground-truth labels.
        notes:
            Free-text annotation.

        Returns
        -------
        TrainingExample
            The newly created and registered example.
        """
        example = TrainingExample(
            correct_fitting_type=correct_fitting_type,
            input_text=input_text,
            image_metadata=image_metadata,
            correct_connection_type=correct_connection_type,
            correct_pressure_class=correct_pressure_class,
            correct_insulation_type=correct_insulation_type,
            notes=notes,
        )
        self._examples.append(example)
        return example

    def add(self, example: TrainingExample) -> None:
        """Register an already-constructed :class:`TrainingExample`."""
        self._examples.append(example)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def examples(self) -> List[TrainingExample]:
        """Return a copy of the current example list."""
        return list(self._examples)

    @property
    def size(self) -> int:
        """Number of examples in the corpus."""
        return len(self._examples)

    def stats(self) -> Dict[str, Any]:
        """Return a summary dict with per-class counts and input types."""
        fitting_counts: Dict[str, int] = {}
        connection_counts: Dict[str, int] = {}
        text_count = 0
        image_count = 0
        for ex in self._examples:
            fitting_counts[ex.correct_fitting_type] = (
                fitting_counts.get(ex.correct_fitting_type, 0) + 1
            )
            if ex.correct_connection_type:
                connection_counts[ex.correct_connection_type] = (
                    connection_counts.get(ex.correct_connection_type, 0) + 1
                )
            if ex.input_text is not None:
                text_count += 1
            if ex.image_metadata is not None:
                image_count += 1
        return {
            "total": self.size,
            "fitting_type_distribution": fitting_counts,
            "connection_type_distribution": connection_counts,
            "text_examples": text_count,
            "image_examples": image_count,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """
        Persist the corpus to a JSON file at *path*.

        Parameters
        ----------
        path:
            File path to write.  Parent directories must already exist.
        """
        payload = {
            "corpus_name": self.name,
            "version": "1.0",
            "examples": [ex.to_dict() for ex in self._examples],
        }
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> TrainingCorpus:
        """
        Load a corpus from a previously saved JSON file.

        Parameters
        ----------
        path:
            Path to the JSON file written by :meth:`save`.

        Returns
        -------
        TrainingCorpus
            Populated corpus.
        """
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        corpus = cls(name=raw.get("corpus_name", "default"))
        for ex_dict in raw.get("examples", []):
            corpus._examples.append(TrainingExample.from_dict(ex_dict))
        return corpus

    def __repr__(self) -> str:
        return f"TrainingCorpus(name={self.name!r}, size={self.size})"


# ---------------------------------------------------------------------------
# ModelTrainer
# ---------------------------------------------------------------------------

# Minimum times a token must appear with a given label before it is emitted
# as a learned keyword.
_MIN_TOKEN_FREQUENCY: int = 1

# Tokens shorter than this (characters) are ignored as noise.
_MIN_TOKEN_LENGTH: int = 3


def _tokenize(text: str) -> List[str]:
    """
    Return lower-cased alphabetic tokens from *text*.

    Uses ``[^\\W\\d_]+`` with ``re.UNICODE`` so that all Unicode alphabetic
    characters (including accented vowels, ñ, and other script letters) are
    captured without an explicit character allow-list.
    """
    return [
        tok for tok in re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)
        if len(tok) >= _MIN_TOKEN_LENGTH
    ]


class ModelTrainer:
    """
    Frequency-based keyword inducer for the HVAC AI module.

    The trainer scans NL descriptions in the corpus, counts how often each
    token appears together with each label class, and emits new keyword →
    label mappings for tokens that are *unambiguous* (appear only with one
    label) and meet the minimum frequency threshold.

    These mappings are returned as :attr:`learned_keywords` and can be
    passed directly to the ``learned_keywords`` parameter of
    :class:`~geometric_engine.ai_module.VisionAIModelGenerator`.

    Attributes
    ----------
    learned_keywords : dict
        After :meth:`fit`, contains:

        ``fitting_type``
            ``{token: fitting_type_value_string}``
        ``connection_type``
            ``{token: connection_type_value_string}``
        ``pressure_class``
            ``{token: pressure_class_value_string}``
        ``insulation_type``
            ``{token: insulation_type_value_string}``
    """

    def __init__(self) -> None:
        self.learned_keywords: Dict[str, Dict[str, str]] = {
            "fitting_type": {},
            "connection_type": {},
            "pressure_class": {},
            "insulation_type": {},
        }
        self._corpus_size: int = 0

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(self, corpus: TrainingCorpus) -> ModelTrainer:
        """
        Learn keyword → label mappings from *corpus*.

        Only NL text examples contribute to keyword learning (image metadata
        dicts do not contain free-text tokens to extract).

        Parameters
        ----------
        corpus:
            Labeled corpus to learn from.

        Returns
        -------
        ModelTrainer
            ``self`` (for method chaining).
        """
        if corpus.size == 0:
            return self

        self._corpus_size = corpus.size

        # Count token → {label_value: frequency}
        fitting_counts: Dict[str, Dict[str, int]] = {}
        connection_counts: Dict[str, Dict[str, int]] = {}
        pressure_counts: Dict[str, Dict[str, int]] = {}
        insulation_counts: Dict[str, Dict[str, int]] = {}

        for ex in corpus.examples:
            if ex.input_text is None:
                continue
            tokens = _tokenize(ex.input_text)
            for tok in tokens:
                # fitting_type
                ft = ex.correct_fitting_type
                fitting_counts.setdefault(tok, {})
                fitting_counts[tok][ft] = fitting_counts[tok].get(ft, 0) + 1

                # connection_type
                if ex.correct_connection_type:
                    ct = ex.correct_connection_type
                    connection_counts.setdefault(tok, {})
                    connection_counts[tok][ct] = connection_counts[tok].get(ct, 0) + 1

                # pressure_class
                if ex.correct_pressure_class:
                    pc = ex.correct_pressure_class
                    pressure_counts.setdefault(tok, {})
                    pressure_counts[tok][pc] = pressure_counts[tok].get(pc, 0) + 1

                # insulation_type
                if ex.correct_insulation_type:
                    it = ex.correct_insulation_type
                    insulation_counts.setdefault(tok, {})
                    insulation_counts[tok][it] = insulation_counts[tok].get(it, 0) + 1

        self.learned_keywords["fitting_type"] = self._induce(fitting_counts)
        self.learned_keywords["connection_type"] = self._induce(connection_counts)
        self.learned_keywords["pressure_class"] = self._induce(pressure_counts)
        self.learned_keywords["insulation_type"] = self._induce(insulation_counts)

        return self

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def accuracy_on_corpus(
        self, corpus: TrainingCorpus
    ) -> Dict[str, float]:
        """
        Measure fitting-type prediction accuracy on a labeled corpus.

        Uses only examples that have *input_text*.  Predictions are made with
        the learned keywords active.

        Parameters
        ----------
        corpus:
            Corpus to evaluate on (may be the same one used for training).

        Returns
        -------
        dict
            ``{"accuracy": float, "correct": int, "total": int}``
        """
        from geometric_engine.ai_module import VisionAIModelGenerator

        ai = VisionAIModelGenerator(learned_keywords=self.learned_keywords)

        correct = 0
        total = 0
        for ex in corpus.examples:
            if ex.input_text is None:
                continue
            try:
                result = ai.process_natural_language(ex.input_text)
                if result["fitting_type"] == ex.correct_fitting_type:
                    correct += 1
            except ValueError:
                pass  # dimensions missing – cannot predict
            total += 1

        accuracy = correct / total if total > 0 else 0.0
        return {
            "accuracy": round(accuracy, 4),
            "correct": correct,
            "total": total,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _induce(
        token_label_counts: Dict[str, Dict[str, int]],
    ) -> Dict[str, str]:
        """
        Return a ``{token: label_value}`` dict for tokens that are
        unambiguous (only one label class seen) and meet the frequency
        threshold.
        """
        result: Dict[str, str] = {}
        for token, label_counts in token_label_counts.items():
            if len(label_counts) != 1:
                continue  # ambiguous token – skip
            label_value, freq = next(iter(label_counts.items()))
            if freq < _MIN_TOKEN_FREQUENCY:
                continue
            result[token] = label_value
        return result

    def __repr__(self) -> str:
        n_kw = sum(len(v) for v in self.learned_keywords.values())
        return (
            f"ModelTrainer(corpus_size={self._corpus_size}, "
            f"learned_keywords={n_kw})"
        )
