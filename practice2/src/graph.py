"""Построение полного графа зависимостей итеративным DFS."""


def analyze(source, package, excluded=""):
    """Построить граф с фильтрацией и защитой от циклов."""
    if excluded and excluded in package:
        raise ValueError("исходный пакет исключён фильтром")
    graph = {}
    visited = set()
    stack = [package]
    while stack:
        name = stack.pop()
        if name in visited:
            continue
        visited.add(name)
        dependencies = source.dependencies(name)
        allowed = [
            dependency for dependency in dependencies
            if not excluded or excluded not in dependency
        ]
        graph[name] = allowed
        for dependency in reversed(allowed):
            if dependency not in visited:
                stack.append(dependency)
    return graph
