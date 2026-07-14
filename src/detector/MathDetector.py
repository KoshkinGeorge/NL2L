import re
from typing import List, Tuple, Dict, Any
from stanza.models.common.doc import Document
from pymorphy3 import MorphAnalyzer


class MathDetector:
    def __init__(self, rules: Dict[int, List[Tuple[str, bool, List[str], List[str]]]], wsize=1):
        self.rules = rules
        self.wsize=wsize
        self.normalizer = MorphAnalyzer()

    def detect(self, doc: Document) -> List[Tuple[int, int]]:
        words = [word for sent in doc.sentences for word in sent.words]
        
        is_math = [False] * len(words)
        is_core_word = [False] * len(words)
        uptrans = [list()] * len(words)
        downtrans = [list()] * len(words)
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\s]', '', word.text)
            normalized = self.normalizer.parse(clean_word)[0].normal_form
            # print(f'{word.text} -> {clean_word} -> {normalized}')
            for priority in sorted(self.rules.keys(), reverse=True):
                found = False
                for regex, is_core, utrans, dtrans in self.rules[priority]:
                    if re.match(regex, normalized):
                        is_math[i] = True
                        if is_core:
                            is_core_word[i] = True
                            # print(f"STRONG MATCH: \t{word.text}")
                        # else:
                            # print(f"WEAK MATCH: \t{word.text}")
                        uptrans[i] = utrans
                        downtrans[i] = dtrans
                        found = True
                        break
                if found:
                    break
        
        # Собираем информацию о зависимостях
        dep_rel = {}
        children = {}
        
        for word in words:
            if word.head != 0:  # 0 - корень
                word_idx = word.id - 1
                head_idx = word.head - 1
                
                dep_rel[word_idx] = (head_idx, word.deprel)
                if head_idx not in children:
                    children[head_idx] = []
                children[head_idx].append((word_idx, word.deprel))
        
        # Распространяем метки от core-слов по их transitions
        for i, word in enumerate(words):
            if not is_math[i]:
                continue
                
            if i in dep_rel:
                parent, deprel = dep_rel[i]
                if deprel in uptrans[i]:
                    is_math[parent] = True
                    # print(f"UPSTREAM TRANSITION: \t{words[parent].text} -> {word.text} ({deprel})")
            
            if i in children:
                for child_idx, deprel in children[i]:
                    if deprel in downtrans[i]:
                        is_math[child_idx] = True
                        # print(f"DOWNSTREAM TRANSITION: \t{word.text} -> {words[child_idx].text} ({deprel})")
        
        # Находим, сращиваем, фильтруем по core
        blocks = []
        start = None
        for i, flag in enumerate(is_math):
            if flag and start is None:
                start = i
            elif not flag and start is not None:
                blocks.append((start, i - 1))
                start = None
        if start is not None:
            blocks.append((start, len(words) - 1))

        # Сращивание
        merged = []
        for s, e in blocks:
            if merged and s - merged[-1][1] - 1 <= self.wsize:
                merged[-1] = (merged[-1][0], e)
            else:
                merged.append((s, e))

        # Только с core
        return [(s, e) for s, e in merged if any(is_core_word[i] for i in range(s, e + 1))]