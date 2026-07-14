import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class NL2L:
    """
    Класс для инференса модели NL2L (преобразование текстового описания формулы в LaTeX).
    """

    def __init__(self, model_dir: str, device: str = None):
        """
        Аргументы:
            model_dir (str): путь к папке с сохранённой моделью и токенизатором.
            device (str, optional): 'cuda' или 'cpu'. Если None, определяется автоматически.
        """
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Загрузка модели с {model_dir} на устройство {self.device}...")

        
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()
        print("Модель успешно загружена.")

    def predict(self, text: str, max_length: int = 128, num_beams: int = 4) -> str:
        """
        Преобразует одно текстовое описание в код LaTeX.

        Аргументы:
            text (str): русское описание формулы.
            max_length (int): максимальная длина генерируемого LaTeX-кода.
            num_beams (int): число лучей при beam search.

        Возвращает:
            str: сгенерированный код LaTeX.
        """
        inputs = self.tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
            )

        latex_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        return latex_code

def predict_batch(self, texts: list, max_length: int = 128, num_beams: int = 4) -> list:
    """
    Преобразует список текстовых описаний в список LaTeX-кодов с использованием батчинга.
    """
    inputs = self.tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )
    inputs = {k: v.to(self.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=num_beams,
            early_stopping=True,
        )

    batch_latex = []
    for output in outputs:
        latex = self.tokenizer.decode(output, skip_special_tokens=True).strip()
        batch_latex.append(latex)
    return batch_latex
