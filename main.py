import argparse


"""
p - parser
a - args
par - parameters
e- errors

python3 main.py --package 0 --repo 0 --version 0 --output 0 --depth 0 --filter 0
"""

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--package', type=str, help='Имя пакета')
    p.add_argument('--repo', type=str, help='URL или путь к репозиторию')
    p.add_argument('--mode', type=str, help='Режим работы с репозиторием (например, online/offline)')
    p.add_argument('--version', type=str, help='Версия пакета')
    p.add_argument('--output', type=str, help='Имя выходного файла изображения')
    p.add_argument('--depth', type=str, help='Максимальная глубина зависимостей')
    p.add_argument('--filter', type=str, dest='filter_str', help='Подстрока фильтра пакетов')

    a = p.parse_args()

    e = []
    if a.package is not None and a.package.strip() == '':
        e.append("Имя пакета не может быть пустым")
    if a.repo is not None and a.repo.strip() == '':
        e.append("Путь/URL к репозиторию не может быть пустым")
    if a.mode is not None and a.mode.strip() == '':
        e.append("Режим не может быть пустым")
    if a.version is not None and a.version.strip() == '':
        e.append("Версия не может быть пустой")
    if a.output is not None and a.output.strip() == '':
        e.append("Имя выходного файла не может быть пустым")
    if a.depth is not None and a.depth.strip() == '':
        e.append("Максимальная глубина зависимостей не может быть пустой")
    if a.filter_str is not None and a.filter_str.strip() == '':
        e.append("Подстрока фильтра пакетов не может быть пустой")

    if e:
        for error in e:
            print(f"Error: {error}")
            exit(1)

    par = []
    if a.package is not None:
        par.append(f"Имя пакета: {a.package}")
    if a.repo is not None:
        par.append(f"Репозиторий: {a.repo}")
    if a.mode is not None:
        par.append(f"Режим: {a.mode}")
    if a.version is not None:
        par.append(f"Версия: {a.version}")
    if a.output is not None:
        par.append(f"Имя выходного файла: {a.output}")
    if a.depth is not None:
        par.append(f"Максимальная глубина зависимостей: {a.depth}")
    if a.filter_str is not None:
        par.append(f"Подстрока фильтра пакетов: {a.filter_str}")

    if par:
        print("Сконфигурированные параметры:")
        for param in par:
            print(param)
    else:
        print("Нет сконфигурированных параметров")

if __name__ == "__main__":
    main()