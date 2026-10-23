"""Integrity-checked per-case evaluation journal, independent of training RNGs."""

from dataclasses import asdict
import hashlib
import ast
import json
import os
from pathlib import Path
import uuid


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def weights_hash(model):
    h = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        tensor = value.detach().cpu().contiguous()
        h.update(encoded([name, str(tensor.dtype), list(tensor.shape)]))
        h.update(tensor.numpy().tobytes())
    return h.hexdigest()


def identity(learner, anchors, encoder, decks, config, max_actions, engine_fingerprint):
    root = Path(__file__).parent

    def function_source(filename, name):
        raw = (root / filename).read_text()
        return next(
            ast.get_source_segment(raw, n)
            for n in ast.parse(raw).body
            if isinstance(n, ast.FunctionDef) and n.name == name
        )

    return dict(
        schema="evaluation-journal-v1",
        engine=engine_fingerprint,
        learner=weights_hash(learner),
        opponents=[(name, weights_hash(model)) for name, model in anchors.items()],
        decks={name: asdict(deck) for name, deck in decks.items()},
        config=asdict(config),
        max_actions=max_actions,
        encoder=asdict(encoder.config),
        encoding_sha256=hashlib.sha256((root / "encoding.py").read_bytes()).hexdigest(),
        model_sha256=hashlib.sha256((root / "model.py").read_bytes()).hexdigest(),
        sampling_sha256=hashlib.sha256(
            (
                function_source("runner.py", "policy_action")
                + function_source("evaluation.py", "heuristic_action")
            ).encode()
        ).hexdigest(),
    )


class EvaluationJournal:
    def __init__(self, root, contract):
        self.key = hashlib.sha256(encoded(contract)).hexdigest()
        self.folder = Path(root) / self.key
        self.folder.mkdir(parents=True, exist_ok=True)
        manifest = self.folder / "contract.json"
        if manifest.exists():
            if encoded(json.loads(manifest.read_text())) != encoded(contract):
                raise ValueError("Evaluation cache identity mismatch")
        else:
            self._atomic(manifest, contract)

    @staticmethod
    def _atomic(path, data):
        raw = encoded(data)
        temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
        try:
            with temporary.open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def case_id(self, opponent, index):
        return f"{self.key}:{opponent}:{index}"

    def _path(self, opponent, index):
        return self.folder / f"case-{opponent:03d}-{index:05d}.json"

    def read(self, opponent, index):
        path = self._path(opponent, index)
        if not path.exists():
            return None
        record = json.loads(path.read_text())
        result = record["result"]
        if (
            record["case_id"] != self.case_id(opponent, index)
            or record["sha256"] != hashlib.sha256(encoded(result)).hexdigest()
        ):
            raise ValueError("Evaluation case integrity failure: " + str(path))
        return result

    def write(self, opponent, index, result):
        self._atomic(
            self._path(opponent, index),
            dict(
                case_id=self.case_id(opponent, index),
                sha256=hashlib.sha256(encoded(result)).hexdigest(),
                result=result,
            ),
        )
