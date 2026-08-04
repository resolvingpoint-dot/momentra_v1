import json
from pathlib import Path

data = json.loads(Path("../ios_copy/momentraTests/Fixtures/business_action_schemas.json").read_text(encoding="utf-8"))


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def field_swift(f: dict, i: int) -> str:
    opts = f.get("options") or []
    if opts:
        items = ", ".join(
            f'.init(value: "{esc(o["value"])}", label: "{esc(o["label"])}")' for o in opts
        )
        opt_lit = f"[{items}]"
    else:
        opt_lit = "nil"
    req = "true" if f.get("required") else "false"
    default = "nil"
    if "default" in f:
        d = f["default"]
        if isinstance(d, bool):
            default = f'"{("true" if d else "false")}"'
        elif d is not None:
            default = f'"{esc(str(d))}"'
    return f"""            BusinessCatalogField(
                fieldKey: "{esc(f["key"])}",
                fieldType: "{esc(f["field_type"])}",
                label: "{esc(f["label"])}",
                required: {req},
                options: {opt_lit},
                defaultValue: {default},
                displayOrder: {i}
            )"""


lines = [
    "import Foundation",
    "",
    "/// Offline/parity schema library — mirrors backend action_catalog field contracts.",
    "enum BusinessActionSchemaLibrary {",
    "    static func fields(forActionId actionId: String) -> [BusinessCatalogField]? {",
    "        schemas[actionId]",
    "    }",
    "",
    "    static func isKnownAction(actionId: String) -> Bool {",
    "        schemas[actionId] != nil",
    "    }",
    "",
    "    /// Explicitly generic note-style actions (backend-defined title+notes).",
    "    static let explicitGenericNoteActionIds: Set<String> = [",
    '        "ops_general_update", "note"',
    "    ]",
    "",
    "    private static let schemas: [String: [BusinessCatalogField]] = [",
]
for aid, meta in data.items():
    lines.append(f'        "{aid}": [')
    lines.append(",\n".join(field_swift(f, i) for i, f in enumerate(meta["fields"])))
    lines.append("        ],")
lines.append("    ]")
lines.append("}")

path = Path("../ios_copy/momentra/Business/actioncenter/BusinessActionSchemaLibrary.swift")
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", path, "bytes", path.stat().st_size)
