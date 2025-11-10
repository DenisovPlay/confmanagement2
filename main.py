import argparse
import urllib.request
import xml.etree.ElementTree as ET

"""
p - parser
a - args
par - parameters
e- errors

python3 main.py --package "com.lumidion:unistore_3" --repo "https://repo1.maven.org/maven2" --version "0.2.0"
python3 main.py --package "org.webjars.npm:swagger-api__apidom-core" --repo "https://repo.maven.apache.org/maven2" --version "0.83.0"
"""

def get_dependencies(group_id, artifact_id, version, repo_url):
    group_path = group_id.replace('.', '/')
    pom_url = f"{repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
    print(f"Загрузка pom из: {pom_url}")
    try:
        with urllib.request.urlopen(pom_url) as response:
            pom_content = response.read()
        root = ET.fromstring(pom_content)
        namespace = {'m': 'http://maven.apache.org/POM/4.0.0'}
        dependencies = root.findall('.//m:dependencies/m:dependency', namespace)
        if not dependencies:
            print("Прямые зависимости не найдены.")
            return
        print("\nПрямые зависимости:")
        for dep in dependencies:
            group_id = dep.find('m:groupId', namespace).text
            artifact_id = dep.find('m:artifactId', namespace).text
            version_element = dep.find('m:version', namespace)
            version = version_element.text if version_element is not None else "не указана"
            print(f"    - ID Группы: {group_id}, ID Артифакта: {artifact_id}, Версия: {version}")
    except urllib.error.URLError as e:
        print(f"Ошибка при загрузке pom-файла: {e.reason}")
    except ET.ParseError as e:
        print(f"Ошибка при разборе XML: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--package', type=str, help='Имя пакета в формате "groupId:artifactId"')
    p.add_argument('--repo', type=str, help='URL репозитория')
    # p.add_argument('--mode', type=str, help='Режим работы с репозиторием (например, online/offline)')
    p.add_argument('--version', type=str, help='Версия пакета')
    # p.add_argument('--output', type=str, help='Имя выходного файла изображения')
    # p.add_argument('--depth', type=str, help='Максимальная глубина зависимостей')
    # p.add_argument('--filter', type=str, dest='filter_str', help='Подстрока фильтра пакетов')

    a = p.parse_args()

    e = []
    if a.package is None or a.package.strip() == '':
        e.append("Имя пакета не может быть пустым")
    elif ':' not in a.package:
        e.append("Имя пакета должно быть в формате 'groupId:artifactId'")
    if a.repo is None or a.repo.strip() == '':
        e.append("URL репозитория не может быть пустым")
    # if a.mode is not None and a.mode.strip() == '':
    #     e.append("Режим не может быть пустым")
    if a.version is None or a.version.strip() == '':
        e.append("Версия не может быть пустой")
    # if a.output is not None and a.output.strip() == '':
    #     e.append("Имя выходного файла не может быть пустым")
    # if a.depth is not None and a.depth.strip() == '':
    #     e.append("Максимальная глубина зависимостей не может быть пустой")
    # if a.filter_str is not None and a.filter_str.strip() == '':
    #     e.append("Подстрока фильтра пакетов не может быть пустой")

    if e:
        for error in e:
            print(f"Ошибка: {error}")
        exit(1)

    par = []
    if a.package is not None:
        par.append(f"Имя пакета: {a.package}")
    if a.repo is not None:
        par.append(f"Репозиторий: {a.repo}")
    # if a.mode is not None:
    #     par.append(f"Режим: {a.mode}")
    if a.version is not None:
        par.append(f"Версия: {a.version}")
    # if a.output is not None:
    #     par.append(f"Имя выходного файла: {a.output}")
    # if a.depth is not None:
    #     par.append(f"Максимальная глубина зависимостей: {a.depth}")
    # if a.filter_str is not None:
    #     par.append(f"Подстрока фильтра пакетов: {a.filter_str}")

    if par:
        #print("Сконфигурированные параметры:")
        #for param in par:
        #    print(param)
        #print("-" * 30)

        try:
            group_id, artifact_id = a.package.split(':', 1)
            get_dependencies(group_id, artifact_id, a.version, a.repo)
        except ValueError:
            print("Ошибка: Неверный формат имени пакета. Используйте 'groupId:artifactId'.")
            exit(1)

    else:
        print("Нет сконфигурированных параметров")

if __name__ == "__main__":
    main()