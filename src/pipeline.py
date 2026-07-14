import re
import yaml
import stanza
import whisper
from typing import List, Dict, Any, Tuple
from detector.MathDetector import MathDetector
from converter.NL2L import NL2L


class Pipeline:
    """
    Единый пайплайн: ASR -> детекция математических блоков -> конвертация в LaTeX.
    """

    def __init__(
        self,
        asr_model_name: str = "base",
        detector_rules_path: str = "./src/detector/markers.yaml",
        converter_model_dir: str = "./src/converter/nl2l-large",
        device: str = None,
    ):
        """
        Аргументы:
            asr_model_name: имя модели Whisper ('tiny','base','small','medium','large')
            detector_rules_path: путь к YAML-файлу с правилами для MathDetector
            converter_model_dir: папка с сохранённой моделью NL2L и токенизатором
            device: устройство для NL2L ('cuda' или 'cpu'), если None – автоопределение
        """
        # 1. ASR (Whisper)
        self.asr = whisper.load_model(asr_model_name)
        print("ASR модель загружена.")

        # 2. Stanza для морфологии и синтаксиса
        self.nlp = stanza.Pipeline("ru", processors="tokenize,pos,lemma,depparse", download_method=None)
        print("Stanza pipeline загружен.")

        # 3. Детектор математических блоков
        rules = self._load_rules(detector_rules_path)
        self.detector = MathDetector(rules)
        print("MathDetector инициализирован.")

        # 4. Конвертер NL2L
        self.converter = NL2L(converter_model_dir, device=device)
        print("NL2L конвертер загружен.")

    def _load_rules(self, path: str) -> Dict[int, List[Tuple[str, bool, List[str], List[str]]]]:
        """Загружает правила из YAML и приводит к формату MathDetector."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        rules = {}
        for priority_str, rule_list in data["rules"].items():
            priority = int(priority_str)
            rules[priority] = []
            for rule in rule_list:
                rules[priority].append((
                    rule["pattern"],
                    rule["is_core"],
                    rule["upstream_transitions"],
                    rule["downstream_transitions"],
                ))
        return rules

    def process_text(self, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        words = [word for sent in doc.sentences for word in sent.words]
        word_texts = [word.text for sent in doc.sentences for word in sent.words]

        blocks = self.detector.detect(doc)
        results = []

        for start, end in blocks:
            block_text = " ".join(word_texts[start:end + 1])
            latex = self.converter.predict(block_text)
            results.append({
                "text": block_text,
                "latex": latex,
                "start": start,
                "end": end,
            })

        transformed_parts = []
        i = 0
        block_idx = 0
        while i < len(word_texts):
            if block_idx < len(blocks) and i == blocks[block_idx][0]:
                latex = results[block_idx]["latex"]
                transformed_parts.append(f"\\({latex}\\)")
                i = blocks[block_idx][1] + 1
                block_idx += 1
            else:
                transformed_parts.append(word_texts[i])
                i += 1

        transformed_text = " ".join(transformed_parts)

        return {
            "blocks": results,
            "full_text": text,
            "transformed_text": transformed_text,
            "word_blocks": blocks,
        }

    def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Принимает путь к аудиофайлу, распознаёт речь и запускает process_text.
        """
        result = self.asr.transcribe(audio_path)
        text = result["text"].strip()
        if not text:
            return {"error": "Речь не обнаружена или файл пуст."}
        return self.process_text(text)