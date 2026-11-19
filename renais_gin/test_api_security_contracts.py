"""Standard-library source contracts for public Django API boundaries."""

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
VIEWS_PATH = ROOT / "core" / "views.py"
URLS_PATH = ROOT / "core" / "urls.py"


def _decorator_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _called_names(node):
    names = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Call):
            if isinstance(item.func, ast.Name):
                names.add(item.func.id)
            elif isinstance(item.func, ast.Attribute):
                names.add(item.func.attr)
    return names


class PublicMovementMetricsContractTests(unittest.TestCase):
    def setUp(self):
        self.views_source = VIEWS_PATH.read_text(encoding="utf-8")
        self.views_tree = ast.parse(self.views_source)
        self.endpoint = next(
            node for node in self.views_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "api_movement_metrics"
        )

    def test_public_metrics_endpoint_is_get_only_and_not_csrf_exempt(self):
        decorators = {_decorator_name(item) for item in self.endpoint.decorator_list}
        self.assertIn("require_GET", decorators)
        self.assertNotIn("csrf_exempt", decorators)

    def test_public_metrics_endpoint_does_not_recalculate_or_write_metrics(self):
        calls = _called_names(self.endpoint)
        self.assertNotIn("update_metrics", calls)
        self.assertIn("filter", calls)
        self.assertIn("first", calls)
        self.assertIn("JsonResponse", calls)

    def test_metrics_route_points_to_the_read_only_endpoint(self):
        urls = URLS_PATH.read_text(encoding="utf-8")
        self.assertIn("api/metrics/", urls)
        self.assertIn("views.api_movement_metrics", urls)


if __name__ == "__main__":
    unittest.main()
