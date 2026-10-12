"""Assembler and Python entry point tests; no Streamlit server or API key."""
import importlib.util
from pathlib import Path
import re
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web_bundle import build_html


class StreamlitPackagingTests(unittest.TestCase):
    def test_embeds_every_module_after_dom_in_order(self):
        html = build_html(ROOT)
        original = (ROOT / "index.html").read_text()
        names = re.findall(r'<script[^>]*src="([^"]+)"', original)
        inline = re.findall(r'<script>\n(.*?)\n</script>', html, re.S)
        self.assertEqual(len(names), len(inline))
        for name, code in zip(names, inline):
            self.assertEqual(code, (ROOT / name).read_text())
        self.assertLess(html.index('id="tbody"'), html.index("<script>"))
        self.assertNotRegex(html, r'<script[^>]*\bsrc=')
        self.assertNotRegex(html, r'<link[^>]*href="styles.css"')
        self.assertIn((ROOT / "styles.css").read_text(), html)

    def test_cwd_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("os.getcwd", return_value=directory):
                self.assertEqual(build_html(), build_html(ROOT))

    def test_missing_assets_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "index.html").write_text(
                '<script src="missing.js"></script><body></body>'
            )
            with self.assertRaisesRegex(ValueError, "Falta un archivo"):
                build_html(Path(directory))

    def test_rejects_asset_outside_repo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (Path(directory) / "outside.js").write_text("alert(1)")
            (root / "index.html").write_text(
                '<script src="../outside.js"></script><body></body>'
            )
            with self.assertRaises(ValueError):
                build_html(root)

    def test_entrypoint_passes_embedded_app_to_streamlit(self):
        calls = []
        fake = types.ModuleType("streamlit")
        fake.set_page_config = lambda **kwargs: calls.append(("config", kwargs))
        fake.iframe = lambda html, **kwargs: calls.append(("iframe", html, kwargs))
        fake.error = lambda message: calls.append(("error", message))
        fake.info = lambda message: calls.append(("info", message))
        fake.stop = lambda: calls.append(("stop",))
        spec = importlib.util.spec_from_file_location("extractor_app", ROOT / "app.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"streamlit": fake}):
            spec.loader.exec_module(module)
            module.main()
            self.assertEqual(calls[0][0], "config")
            self.assertEqual(calls[1][0], "iframe")
            self.assertEqual(calls[1][2]["height"], "content")
            self.assertIn('id="classifyBtn"', calls[1][1])
            calls.clear()
            with patch.object(module, "build_html", side_effect=ValueError("faltan módulos")):
                module.main()
            self.assertEqual([c[0] for c in calls], ["config", "error", "info", "stop"])


if __name__ == "__main__":
    unittest.main()
