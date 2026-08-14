"""Self-check for project-config discovery.
Run: python bin/test_project_config.py"""

import tempfile
from pathlib import Path

from profile_mcp.cli import find_project_config, load_mcp_keys


def make_tree(base: Path, rel: str, content: str = '{"mcp": {}}') -> Path:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)

    # nearest opencode.json wins, walking up from a nested cwd
    nested = make_tree(root, "project/sub/open-code-tree", "")
    make_tree(root, "project/opencode.json")
    found = find_project_config(nested)
    assert found == root / "project/opencode.json", found

    # jsonc candidate next in priority
    make_tree(root, "jsonc-project/opencode.jsonc", '{"mcp": {}}')
    found = find_project_config(root / "jsonc-project")
    assert found == root / "jsonc-project/opencode.jsonc", found

    # .opencode/opencode.json last
    make_tree(root, "dot-dir/.opencode/opencode.json")
    found = find_project_config(root / "dot-dir")
    assert found == root / "dot-dir/.opencode/opencode.json", found

    # no config anywhere above -> None (use a bare dir under tmp)
    empty = root / "nothing-here"
    empty.mkdir()
    assert find_project_config(empty) is None

    # load_mcp_keys strips jsonc comments
    commented = make_tree(
        root, "commented/opencode.jsonc",
        '{\n  // a comment\n  "mcp": {\n    "svc": { "type": "local" } /* inline */\n  }\n}\n',
    )
    keys = load_mcp_keys(commented)
    assert keys == {"svc": {"type": "local"}}, keys

print("ok")
