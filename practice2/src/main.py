"""CLI-точка входа для первых трёх этапов практики №2."""

import sys

from .config import ConfigError, parser_for_stage, validate_config


def main(argv=None):
    """Проверить параметры и выполнить доступный этап."""
    parser = parser_for_stage(3)
    args = parser.parse_args(argv)
    try:
        validate_config(args)
        from .graph import analyze
        from .repository import create_source
        source = create_source(args.repository, args.test_mode)
        graph = analyze(source, args.package, args.filter)
    except (ConfigError, ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(f"package: {args.package}")
    print(f"repository: {args.repository}")
    print(f"test_mode: {args.test_mode}")
    print(f"output: {args.output}")
    print(f"filter: {args.filter}")
    print("Граф зависимостей (пакет -> прямые зависимости):")
    for name, dependencies in graph.items():
        print(f"{name}: {', '.join(dependencies) or '(нет)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
