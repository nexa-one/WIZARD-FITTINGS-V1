"""
Tests for the training module.

Covers: TrainingExample, TrainingCorpus, ModelTrainer, and integration
with VisionAIModelGenerator (learned_keywords + record_feedback).
"""

import json
import tempfile
from pathlib import Path

import pytest

from geometric_engine.ai_module import VisionAIModelGenerator
from geometric_engine.models import (
    ConnectionType,
    FittingType,
    InsulationType,
    PressureClass,
)
from geometric_engine.training import (
    ModelTrainer,
    TrainingCorpus,
    TrainingExample,
    _tokenize,
)


# ---------------------------------------------------------------------------
# TrainingExample
# ---------------------------------------------------------------------------


class TestTrainingExample:
    def test_text_example_created(self):
        ex = TrainingExample(
            correct_fitting_type="straight",
            input_text="24x12 straight duct",
        )
        assert ex.correct_fitting_type == "straight"
        assert ex.input_text == "24x12 straight duct"

    def test_image_example_created(self):
        ex = TrainingExample(
            correct_fitting_type="elbow_90",
            image_metadata={"fitting_type": "elbow_90", "width": 24, "height": 12},
        )
        assert ex.image_metadata is not None

    def test_no_input_raises(self):
        with pytest.raises(ValueError, match="input_text or image_metadata"):
            TrainingExample(correct_fitting_type="straight")

    def test_invalid_fitting_type_raises(self):
        with pytest.raises(ValueError):
            TrainingExample(
                correct_fitting_type="banana_fitting",
                input_text="banana duct",
            )

    def test_invalid_connection_type_raises(self):
        # "welded" is not a valid ConnectionType value; the constructor
        # should reject it immediately via ConnectionType("welded").
        with pytest.raises(ValueError, match="welded"):
            TrainingExample(
                correct_fitting_type="straight",
                input_text="24x12 duct",
                correct_connection_type="welded",
            )

    def test_invalid_pressure_class_raises(self):
        with pytest.raises(ValueError):
            TrainingExample(
                correct_fitting_type="straight",
                input_text="24x12 duct",
                correct_pressure_class="999",
            )

    def test_optional_fields_none_by_default(self):
        ex = TrainingExample(
            correct_fitting_type="tee", input_text="24x12 tee"
        )
        assert ex.correct_connection_type is None
        assert ex.correct_pressure_class is None
        assert ex.correct_insulation_type is None
        assert ex.notes is None

    def test_created_at_is_set(self):
        ex = TrainingExample(
            correct_fitting_type="straight", input_text="24x12"
        )
        assert ex.created_at  # non-empty ISO string

    def test_to_dict_round_trip(self):
        ex = TrainingExample(
            correct_fitting_type="reducer",
            input_text="24x12 reducer",
            correct_connection_type="tdc",
            notes="test",
        )
        d = ex.to_dict()
        ex2 = TrainingExample.from_dict(d)
        assert ex2.correct_fitting_type == ex.correct_fitting_type
        assert ex2.correct_connection_type == ex.correct_connection_type
        assert ex2.notes == ex.notes

    def test_all_fitting_types_valid(self):
        for ft in FittingType:
            ex = TrainingExample(
                correct_fitting_type=ft.value, input_text="dummy 24x12"
            )
            assert ex.correct_fitting_type == ft.value


# ---------------------------------------------------------------------------
# TrainingCorpus
# ---------------------------------------------------------------------------


class TestTrainingCorpus:
    def test_empty_corpus(self):
        corpus = TrainingCorpus()
        assert corpus.size == 0
        assert corpus.examples == []

    def test_add_example_increases_size(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="straight", input_text="24x12 straight"
        )
        assert corpus.size == 1

    def test_add_accepts_prebuilt_example(self):
        corpus = TrainingCorpus()
        ex = TrainingExample(
            correct_fitting_type="tee", input_text="24x12 tee fitting"
        )
        corpus.add(ex)
        assert corpus.size == 1

    def test_examples_returns_copy(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="straight", input_text="24x12"
        )
        lst = corpus.examples
        lst.append(None)  # type: ignore[arg-type]
        assert corpus.size == 1  # internal list unchanged

    def test_stats_counts_by_fitting_type(self):
        corpus = TrainingCorpus()
        corpus.add_example(correct_fitting_type="straight", input_text="24x12 straight")
        corpus.add_example(correct_fitting_type="straight", input_text="18x10 straight")
        corpus.add_example(correct_fitting_type="elbow_90", input_text="24x12 90")
        stats = corpus.stats()
        assert stats["total"] == 3
        assert stats["fitting_type_distribution"]["straight"] == 2
        assert stats["fitting_type_distribution"]["elbow_90"] == 1

    def test_stats_text_vs_image(self):
        corpus = TrainingCorpus()
        corpus.add_example(correct_fitting_type="straight", input_text="24x12")
        corpus.add_example(
            correct_fitting_type="elbow_90",
            image_metadata={"fitting_type": "elbow_90", "width": 24, "height": 12},
        )
        stats = corpus.stats()
        assert stats["text_examples"] == 1
        assert stats["image_examples"] == 1

    def test_save_and_load_roundtrip(self):
        corpus = TrainingCorpus(name="test-corpus")
        corpus.add_example(
            correct_fitting_type="reducer",
            input_text="24x12 reducer",
            correct_connection_type="tdc",
            notes="unit test",
        )
        corpus.add_example(
            correct_fitting_type="tee",
            input_text="24x12 tee",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "corpus.json"
            corpus.save(path)

            assert path.exists()
            raw = json.loads(path.read_text())
            assert raw["corpus_name"] == "test-corpus"
            assert len(raw["examples"]) == 2

            loaded = TrainingCorpus.load(path)
            assert loaded.name == "test-corpus"
            assert loaded.size == 2
            assert loaded.examples[0].correct_fitting_type == "reducer"
            assert loaded.examples[0].correct_connection_type == "tdc"
            assert loaded.examples[1].correct_fitting_type == "tee"

    def test_repr(self):
        corpus = TrainingCorpus(name="my-corpus")
        assert "my-corpus" in repr(corpus)
        assert "0" in repr(corpus)


# ---------------------------------------------------------------------------
# Tokenizer helper
# ---------------------------------------------------------------------------


class TestTokenize:
    def test_basic_tokens(self):
        tokens = _tokenize("24x12 straight duct")
        assert "straight" in tokens
        assert "duct" in tokens

    def test_short_tokens_excluded(self):
        tokens = _tokenize("a 24x12 to duct")
        for tok in tokens:
            assert len(tok) >= 3

    def test_spanish_tokens(self):
        tokens = _tokenize("codo 90 grados ducto")
        assert "codo" in tokens
        assert "grados" in tokens
        assert "ducto" in tokens

    def test_numbers_excluded(self):
        tokens = _tokenize("24x12 straight")
        for tok in tokens:
            assert not tok.isdigit()


# ---------------------------------------------------------------------------
# ModelTrainer
# ---------------------------------------------------------------------------


class TestModelTrainer:
    def test_empty_corpus_returns_empty_mappings(self):
        trainer = ModelTrainer()
        trainer.fit(TrainingCorpus())
        for v in trainer.learned_keywords.values():
            assert v == {}

    def test_learns_new_fitting_keyword(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo 90 grados 24x12",
        )
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo giro 18x12",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        # "codo" should be learned as pointing to elbow_90
        assert "codo" in trainer.learned_keywords["fitting_type"]
        assert trainer.learned_keywords["fitting_type"]["codo"] == "elbow_90"

    def test_ambiguous_token_not_learned(self):
        corpus = TrainingCorpus()
        # "codo" appears for both elbow_90 and elbow_45 → ambiguous
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo 90 24x12",
        )
        corpus.add_example(
            correct_fitting_type="elbow_45",
            input_text="codo 45 24x12",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        assert "codo" not in trainer.learned_keywords["fitting_type"]

    def test_learns_connection_type_keyword(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="straight",
            input_text="ducto recto 24x12 bridado",
            correct_connection_type="tdc",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        assert trainer.learned_keywords["connection_type"].get("bridado") == "tdc"

    def test_learned_keywords_dict_structure(self):
        trainer = ModelTrainer()
        trainer.fit(TrainingCorpus())
        assert set(trainer.learned_keywords.keys()) == {
            "fitting_type", "connection_type", "pressure_class", "insulation_type"
        }

    def test_fit_returns_self(self):
        trainer = ModelTrainer()
        result = trainer.fit(TrainingCorpus())
        assert result is trainer

    def test_repr_after_training(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo 90 24x12",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        r = repr(trainer)
        assert "ModelTrainer" in r
        assert "corpus_size=1" in r

    def test_accuracy_all_correct(self):
        corpus = TrainingCorpus()
        # Add enough examples that "codo" is unambiguously elbow_90
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo 90 grados 24x12",
        )
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo angulo 18x12",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        metrics = trainer.accuracy_on_corpus(corpus)
        assert isinstance(metrics["accuracy"], float)
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert metrics["total"] == 2

    def test_accuracy_image_only_examples_not_counted(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="straight",
            image_metadata={"fitting_type": "straight", "width": 24, "height": 12},
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        metrics = trainer.accuracy_on_corpus(corpus)
        # image-only examples have no NL text, so they are skipped entirely
        assert metrics["total"] == 0
        assert metrics["correct"] == 0
        assert metrics["accuracy"] == 0.0

    def test_accuracy_missing_dimensions_handled(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="straight",
            input_text="just a duct no dimensions",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        # Should not raise; missing dimensions → skip
        metrics = trainer.accuracy_on_corpus(corpus)
        assert metrics["total"] == 1


# ---------------------------------------------------------------------------
# Integration: VisionAIModelGenerator with learned_keywords
# ---------------------------------------------------------------------------


class TestLearnedKeywordsIntegration:
    def test_learned_fitting_type_used(self):
        """AI trained on 'codo' → elbow_90 should classify correctly."""
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo 90 grados 24x12",
        )
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo angulo 18x12",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)

        ai = VisionAIModelGenerator(learned_keywords=trainer.learned_keywords)
        result = ai.process_natural_language("codo 24x12")
        assert result["fitting_type"] == "elbow_90"

    def test_builtin_keywords_still_work_after_training(self):
        """Existing 'straight' keyword must survive a training pass."""
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="elbow_90",
            input_text="codo 90 24x12",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)

        ai = VisionAIModelGenerator(learned_keywords=trainer.learned_keywords)
        result = ai.process_natural_language("24x12 straight duct")
        assert result["fitting_type"] == "straight"

    def test_no_learned_keywords_behaves_as_before(self):
        """Without training, behaviour is unchanged."""
        ai_plain = VisionAIModelGenerator()
        ai_trained = VisionAIModelGenerator(learned_keywords={})
        r1 = ai_plain.process_natural_language("24x12 straight duct")
        r2 = ai_trained.process_natural_language("24x12 straight duct")
        assert r1["fitting_type"] == r2["fitting_type"]

    def test_learned_connection_type_used(self):
        corpus = TrainingCorpus()
        corpus.add_example(
            correct_fitting_type="straight",
            input_text="ducto recto 24x12 bridado",
            correct_connection_type="tdc",
        )
        trainer = ModelTrainer()
        trainer.fit(corpus)
        ai = VisionAIModelGenerator(learned_keywords=trainer.learned_keywords)
        result = ai.process_natural_language("ducto 24x12 bridado")
        # "bridado" learned → tdc
        assert result["connection_type"] == "tdc"


# ---------------------------------------------------------------------------
# Integration: VisionAIModelGenerator.record_feedback
# ---------------------------------------------------------------------------


class TestRecordFeedback:
    def setup_method(self):
        self.ai = VisionAIModelGenerator()

    def test_returns_training_example(self):
        ex = self.ai.record_feedback(
            correct_fitting_type="elbow_90",
            input_text="codo 90 24x12",
        )
        assert isinstance(ex, TrainingExample)
        assert ex.correct_fitting_type == "elbow_90"
        assert ex.input_text == "codo 90 24x12"

    def test_example_can_be_added_to_corpus(self):
        ex = self.ai.record_feedback(
            correct_fitting_type="tee",
            input_text="te 24x12",
            notes="Spanish input",
        )
        corpus = TrainingCorpus()
        corpus.add(ex)
        assert corpus.size == 1
        assert corpus.examples[0].notes == "Spanish input"

    def test_full_workflow(self):
        """End-to-end: predict → feedback → train → improved prediction."""
        corpus = TrainingCorpus()
        ai = VisionAIModelGenerator()

        # Simulate 3 corrections for "codo" → elbow_90
        for phrase in ("codo 90 24x12", "codo giro 18x10", "codo doblado 30x20"):
            ex = ai.record_feedback(
                correct_fitting_type="elbow_90",
                input_text=phrase,
            )
            corpus.add(ex)

        trainer = ModelTrainer()
        trainer.fit(corpus)

        ai2 = VisionAIModelGenerator(learned_keywords=trainer.learned_keywords)
        result = ai2.process_natural_language("codo 24x12")
        assert result["fitting_type"] == "elbow_90"

    def test_record_feedback_with_image_metadata(self):
        ex = self.ai.record_feedback(
            correct_fitting_type="reducer",
            image_metadata={"fitting_type": "straight", "width": 24, "height": 12},
            notes="wrong auto-detection",
        )
        assert ex.image_metadata is not None
        assert ex.correct_fitting_type == "reducer"

    def test_record_feedback_invalid_fitting_type_raises(self):
        with pytest.raises(ValueError):
            self.ai.record_feedback(
                correct_fitting_type="invalid_type",
                input_text="24x12 duct",
            )
