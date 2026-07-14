import sys
from formal_lang.lark import Lark
from lark.visitors import CollapseAmbiguities
from lark.tree import pydot__tree_to_png

def find_non_overlapping_blocks(tokens, parser, start=0, end=None):
    """
    Рекурсивно ищет блоки в порядке убывания длины внутри среза tokens[start:end].
    Возвращает список кортежей (i, j, sub, tree) для непересекающихся блоков,
    отсортированных по позиции.
    """
    if end is None:
        end = len(tokens)
    if start >= end:
        return []

    best_blocks = []
    for length in range(end - start, 0, -1):
        for i in range(start, end - length + 1):
            j = i + length
            sub = ' '.join(tokens[i:j])
            try:
                tree = parser.parse(sub)
                # Нашли блок – фиксируем его
                block = (i, j, sub, tree)
                # Рекурсивно обрабатываем левую и правую части
                left_blocks = find_non_overlapping_blocks(tokens, parser, start, i)
                right_blocks = find_non_overlapping_blocks(tokens, parser, j, end)
                # Объединяем: сначала левые, потом текущий, потом правые
                return left_blocks + [block] + right_blocks
            except Exception:
                continue
    # Если ни один блок не найден, возвращаем пустой список
    return []

def main():
    # Загружаем парсер из готовых файлов grammar/
    parser = Lark.open(
        './src/parser/grammar/math.lark',
        parser='earley'
    )

    # Получаем входной текст
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        text = input("Введите предложение на русском: ")

    tokens = text.split()
    print(f"\nИсходный текст: {text}")
    print(f"Токенов: {len(tokens)}")
    print("=" * 60)

    blocks = find_non_overlapping_blocks(tokens, parser)

    if not blocks:
        print("Не найдено ни одного блока, соответствующего грамматике.")
        return

    print(f"Найдено {len(blocks)} непересекающихся блоков:\n")

    for idx, (i, j, sub, tree) in enumerate(blocks, 1):
        print(f"--- Блок {idx} ---")
        print(f"Позиция токенов: с {i} по {j-1} (всего {j-i} токенов)")
        print(f"Подстрока: '{sub}'")
        
        trees = list(CollapseAmbiguities().transform(tree))
        
        if len(trees) == 1:
            print("Дерево разбора (однозначное):")
            print(tree.pretty())
            pydot__tree_to_png(trees[0], "./trees/parse_tree.png", rankdir='TB')

        else:
            print(f"Найдено {len(trees)} возможных деревьев разбора (неоднозначность):")
            for k, alt_tree in enumerate(trees, 1):
                print(f"--- Вариант {k} ---")
                print(alt_tree.pretty())
                pydot__tree_to_png(alt_tree, f"./trees/parse_tree_{k}.png", rankdir='TB')
        print("-" * 50)

if __name__ == "__main__":
    main()

# 858 вариантов:  икс минус один делить на игрек плюс альфа на три плюс четыре делить на сигма минус бэта
# 4862 варианта: a минус b минус c минус d минус e минус f минус g минус h минус i минус j