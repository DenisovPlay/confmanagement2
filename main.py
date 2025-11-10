import argparse
import urllib.request
import xml.etree.ElementTree as ET
import os
import sys

"""
p - parser
a - args
par - parameters
e- errors

python3 main.py --package "com.lumidion:unistore_3" --repo "https://repo1.maven.org/maven2" --version "0.2.0" --depth "2" --filter "test"
python3 main.py --package "A" --repo "test_graph.txt" --mode "test" --version "1.0" --depth=8
"""

def parse_test_graph(file_path):
    """Парсит тестовый граф из файла в формате:
    A: B C D
    B: E F
    """
    graph = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    node, deps = line.split(':', 1)
                    node = node.strip()
                    deps_list = [d.strip() for d in deps.split() if d.strip()]
                    graph[node] = deps_list
        return graph
    except Exception as e:
        print(f"Ошибка чтения тестового файла: {e}")
        sys.exit(1)

def fetch_pom_dependencies(group_id, artifact_id, version, repo_url):
    """Получает прямые зависимости из POM-файла"""
    try:
        group_path = group_id.replace('.', '/')
        repo_url = repo_url.rstrip('/')
        pom_url = f"{repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        
        with urllib.request.urlopen(pom_url, timeout=10) as response:
            pom_content = response.read()
        
        root = ET.fromstring(pom_content)
        namespace = {'m': 'http://maven.apache.org/POM/4.0.0'}
        dependencies = root.findall('.//m:dependencies/m:dependency', namespace)
        
        result = []
        for dep in dependencies:
            dep_group = dep.find('m:groupId', namespace)
            dep_artifact = dep.find('m:artifactId', namespace)
            dep_version = dep.find('m:version', namespace)
            
            if dep_group is not None and dep_artifact is not None:
                dep_group_text = dep_group.text.strip()
                dep_artifact_text = dep_artifact.text.strip()
                dep_version_text = dep_version.text.strip() if dep_version is not None else version
                
                result.append((dep_group_text, dep_artifact_text, dep_version_text))
        
        return result
    except Exception as e:
        print(f"Ошибка получения зависимостей для {group_id}:{artifact_id}:{version}: {e}")
        return []

def build_dependency_graph(package_name, repo_url, version, max_depth, filter_str, visited=None, current_depth=0, mode="online", test_graph=None):
    if visited is None:
        visited = set()
    
    if current_depth > max_depth:
        return {}
    
    if package_name in visited:
        print(f"  {'  ' * current_depth} Циклическая зависимость: {package_name}")
        return {}
    
    visited.add(package_name)
    
    result = {package_name: []}
    
    if filter_str and filter_str in package_name:
        print(f"  {'  ' * current_depth} Пропущен из-за фильтра: {package_name}")
        visited.remove(package_name)
        return {}
    
    print(f"  {'  ' * current_depth} {package_name} (глубина {current_depth}/{max_depth})")
    
    dependencies = []
    if mode == "test":
        if test_graph and package_name in test_graph:
            dependencies = [(dep, "", "") for dep in test_graph[package_name]]
    else:
        if ':' in package_name:
            group_id, artifact_id = package_name.split(':', 1)
            dependencies = fetch_pom_dependencies(group_id, artifact_id, version, repo_url)
            dependencies = [(f"{dep[0]}:{dep[1]}", dep[1], dep[2]) for dep in dependencies]
    
    for dep, artifact_id, dep_version in dependencies:
        if not dep.strip():
            continue
            
        dep_result = build_dependency_graph(
            package_name=dep,
            repo_url=repo_url,
            version=dep_version,
            max_depth=max_depth,
            filter_str=filter_str,
            visited=visited.copy(),
            current_depth=current_depth + 1,
            mode=mode,
            test_graph=test_graph
        )
        
        if dep_result:
            result[package_name].append(dep_result)
    
    visited.remove(package_name)
    return result

def print_dependency_graph(graph, indent=0):
    for package, deps in graph.items():
        print("  " * indent + f" {package}")
        for dep in deps:
            print_dependency_graph(dep, indent + 1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--package', type=str, help='Имя пакета в формате "groupId:artifactId" для режима online или имя пакета для режима test')
    p.add_argument('--repo', type=str, help='URL репозитория или путь к файлу с описанием графа для режима test')
    p.add_argument('--mode', type=str, default='online', choices=['online', 'test'], help='Режим работы: online или test')
    p.add_argument('--version', type=str, help='Версия пакета')
    p.add_argument('--output', type=str, help='Имя выходного файла изображения')
    p.add_argument('--depth', type=int, default=1, help='Максимальная глубина зависимостей')
    p.add_argument('--filter', type=str, dest='filter_str', help='Подстрока фильтра пакетов')

    a = p.parse_args()

    e = []
    if a.package is None or a.package.strip() == '':
        e.append("Имя пакета не может быть пустым")
    if a.repo is None or a.repo.strip() == '':
        e.append("Репозиторий не может быть пустым")
    if a.version is None or a.version.strip() == '':
        e.append("Версия не может быть пустой")
    if a.depth < 0:
        e.append("Глубина должна быть неотрицательным числом")
    if a.mode == "test" and not os.path.exists(a.repo):
        e.append(f"Файл тестового репозитория не существует: {a.repo}")

    if e:
        for error in e:
            print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)

    """
    par = []
    if a.package is not None:
        par.append(f"Имя пакета: {a.package}")
    if a.repo is not None:
        par.append(f"Репозиторий: {a.repo}")
    if a.version is not None:
        par.append(f"Версия: {a.version}")

    if par:
        print("Сконфигурированные параметры:")
        for param in par:
            print(param)
        print("-" * 30)

        try:
            group_id, artifact_id = a.package.split(':', 1)
            get_dependencies(group_id, artifact_id, a.version, a.repo)
        except ValueError:
            print("Ошибка: Неверный формат имени пакета. Используйте 'groupId:artifactId'.")
            exit(1)

    else:
        print("Нет сконфигурированных параметров")
    """

    print(f"Анализ зависимостей {a.mode}")
    
    test_graph = None
    if a.mode == "test":
        test_graph = parse_test_graph(a.repo)
        print(f"Загружен тестовый граф из файла: {a.repo}")
    
    dependency_graph = build_dependency_graph(
        package_name=a.package,
        repo_url=a.repo,
        version=a.version,
        max_depth=a.depth,
        filter_str=a.filter_str,
        mode=a.mode,
        test_graph=test_graph
    )
    
    print("\n" + "="*30 + "\nГраф зависимостей:\n")
    if dependency_graph:
        print_dependency_graph(dependency_graph)
    else:
        print("Граф зависимостей пуст")

if __name__ == "__main__":
    main()