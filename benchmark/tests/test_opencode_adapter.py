"""Offline tests of the isolated OpenCode v2 adapter.

Run with ``python -B -m unittest discover -s benchmark/tests -p test_opencode_adapter.py``.
The real CLI is used for runtime discovery; a test launcher supplies the recorded
OpenCode JSON protocol for model turns. Bubblewrap denies external network access
even if the adapter is broken. No real credentials are used.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODEL = "opencode/beam-free"
FIXTURE_URL = "http://127.0.0.1:18999/v1"
VERSION = "2.3.2"
AGENT = "benchmark-untrusted-agent"
MARKER = "BENCHMARK_UNTRUSTED_INSTRUCTION_MARKER"
SESSION = "ses_fixture_first_turn"
TURNS = ("First fixture question?", "Follow-up: use the same session.")
ANSWERS = ("First fixture answer.", "Second fixture answer.")
ISOLATION_ERROR = r"(?i)\b(?:isolat\w*|contaminat\w*|unexpected (?:config\w*|agent|instruction))\b"


def installed_opencode():
    """Prefer the installed native executable over the user-home-dependent shim."""
    mise = shutil.which("mise")
    if mise:
        result = subprocess.run(
            [mise, "where", "npm:@opencode/cli"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            packages = Path(result.stdout.strip()) / "node_modules/.mise"
            for executable in sorted(packages.glob("@opencode+cli-linux-*@*/node_modules/"
                                                    "@opencode/cli-linux-*/bin/opencode")):
                if "-baseline" not in str(executable) and "-musl" not in str(executable):
                    return executable
    path = shutil.which("opencode")
    return Path(path).resolve() if path else None


class OpenCodeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bwrap = shutil.which("bwrap")
        cls.opencode = installed_opencode()
        if not cls.bwrap or not cls.opencode:
            raise unittest.SkipTest("OpenCode and bubblewrap are required for no-egress CLI tests")
        probe = subprocess.run(
            [cls.bwrap, "--unshare-net", "--unshare-pid", "--ro-bind", "/", "/", "/bin/true"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if probe.returncode != 0:
            raise unittest.SkipTest(f"Cannot create the no-egress test sandbox: {probe.stderr.strip()}")

    def setUp(self):
        base = Path("/tmp/opencode")
        temp = tempfile.TemporaryDirectory(
            dir=base if base.is_dir() else "/tmp", prefix="benchmark-opencode-",
        )
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.outer = self.root / "outer"
        self.home = self.root / "home"
        self.tmp = self.root / "tmp"
        self.outer.mkdir()
        self.home.mkdir()
        self.tmp.mkdir()
        self.log = self.root / "inference.jsonl"
        self.env = {
            "PATH": os.defpath,
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "OPENCODE_DISABLE_AUTOUPDATE": "true",
            "OPENCODE_DISABLE_MODELS_FETCH": "true",
            "OPENCODE_DISABLE_LSP_DOWNLOAD": "true",
            **{
                f"XDG_{key}_HOME": str(self.root / key.lower())
                for key in ("CONFIG", "DATA", "STATE", "CACHE")
            },
        }
        self.launcher()

    def launch(self, *args, cwd=None):
        cwd = cwd or self.outer
        return subprocess.run(
            [
                self.bwrap, "--unshare-net", "--unshare-pid", "--die-with-parent",
                "--new-session", "--ro-bind", "/", "/", "--tmpfs", "/tmp", "--tmpfs", "/run",
                "--bind", str(self.root), str(self.root), "--dev", "/dev", "--proc", "/proc",
                "--chdir", str(cwd), *map(str, args),
            ],
            env=self.env, cwd=cwd, input="", capture_output=True, text=True, timeout=30,
            check=False,
        )

    def launcher(self, contamination=None):
        """Observe or replace only inference; all discovery goes to the real CLI."""
        launcher = self.root / "opencode-fixture"
        script = f"""\
            import json
            import os
            from pathlib import Path
            import subprocess
            import sys

            args = sys.argv[1:]
            binary = {str(self.opencode)!r}
            contamination = {contamination!r}
            if contamination and args and args[0] == 'serve':
                config_path = Path(os.environ['XDG_CONFIG_HOME']) / 'opencode/opencode.json'
                config = json.loads(config_path.read_text(encoding='utf-8'))
                if contamination == 'instructions':
                    marker = config_path.parent / 'AGENTS.md'
                    marker.write_text({MARKER!r} + '\\n', encoding='utf-8')
                    config['instructions'] = [str(marker)]
                else:
                    config['agent'] = {{{AGENT!r}: {{'mode': 'primary', 'prompt': {MARKER!r}}}}}
                config_path.write_text(json.dumps(config), encoding='utf-8')
            if contamination and args and args[0] == 'api' and 'config.get' in args:
                results = {{}}
                for operation in ('config.get', 'agent.list'):
                    command = [binary, *args]
                    command[command.index('config.get')] = operation
                    result = subprocess.run(command, capture_output=True, text=True, check=False)
                    results[operation] = {{'returncode': result.returncode, 'stdout': result.stdout,
                                          'stderr': result.stderr}}
                Path({str(self.root / "diagnostic.json")!r}).write_text(
                    json.dumps(results), encoding='utf-8')
                sys.stdout.write(results['config.get']['stdout'])
                sys.stderr.write(results['config.get']['stderr'])
                sys.exit(results['config.get']['returncode'])
            if args and args[0] == 'run':
                with Path({str(self.log)!r}).open('a', encoding='utf-8') as log:
                    print(json.dumps({{'argv': args, 'cwd': os.getcwd()}}), file=log)
                answers = dict(zip({TURNS!r}, {ANSWERS!r}))
                text = next((answers[arg] for arg in args if arg in answers), None)
                if text is None:
                    sys.exit('Unexpected inference invocation in test')
                for kind, part in (
                    ('step_start', {{'type': 'step-start'}}),
                    ('text', {{'type': 'text', 'text': text}}),
                    ('step_finish', {{'type': 'step-finish', 'reason': 'stop'}}),
                ):
                    print(json.dumps({{'type': kind, 'timestamp': 1, 'sessionID': {SESSION!r},
                                      'part': {{'sessionID': {SESSION!r}, **part}}}}))
            else:
                os.execv(binary, [binary, *args])
        """
        launcher.write_text(f"#!{sys.executable}\n" + textwrap.dedent(script), encoding="utf-8")
        launcher.chmod(0o700)
        self.env["BENCHMARK_OPENCODE_BIN"] = str(launcher)
        # A non-ELF launcher is only permitted for the offline loopback fixture.
        self.env["BENCHMARK_OPENCODE_LOOPBACK_URL"] = FIXTURE_URL
        return launcher

    def cli_doctor(self, *args):
        return self.launch(sys.executable, "-B", "-m", "benchmark", "doctor",
                           "--model", MODEL, "--json", *args)

    def report(self, result):
        self.assertEqual(
            result.returncode, 0,
            "Isolated OpenCode doctor is unavailable or failed:\n"
            f"stdout={result.stdout!r}\nstderr={result.stderr!r}",
        )
        report = json.loads(result.stdout)
        self.assertIs(report["ok"], True)
        self.assertEqual(report["model"], MODEL)
        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["agent"], "build")
        workspace = Path(report["workspace"]).resolve()
        self.assertTrue(workspace.is_absolute())
        self.assertFalse(workspace.is_relative_to(ROOT), workspace)
        self.assertFalse(workspace.is_relative_to(self.outer), workspace)
        self.assertNotIn(MARKER, result.stdout + result.stderr)
        self.assertNotIn(AGENT, result.stdout + result.stderr)
        self.assertFalse(self.log.exists(), "Doctor must not send a model turn")
        return report

    def contamination(self, directory, *, instructions=True, agent=True):
        directory.mkdir(parents=True, exist_ok=True)
        config = {}
        if instructions:
            marker = directory / "AGENTS.md"
            marker.write_text(f"{MARKER}\n", encoding="utf-8")
            config["instructions"] = [str(marker)]
        if agent:
            config["agent"] = {AGENT: {"mode": "primary", "prompt": MARKER}}
        path = directory / "opencode.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    def test_real_doctor_ignores_outer_instructions_and_custom_agent_and_denies_tools(self):
        config = self.contamination(Path(self.env["XDG_CONFIG_HOME"]) / "opencode")
        (self.outer / "AGENTS.md").write_text(f"{MARKER}\n", encoding="utf-8")
        self.env["OPENCODE_CONFIG"] = str(config)
        # Positive control: the same real OpenCode binary sees both markers if
        # launched with the test-owned outer environment rather than the adapter.
        control = self.launch(self.opencode, "debug", "config", "--standalone")
        self.assertEqual(control.returncode, 0, control.stdout + control.stderr)
        self.assertIn(AGENT, control.stdout)
        self.assertIn(str(config.parent / "AGENTS.md"), control.stdout)
        report = self.report(self.cli_doctor())
        self.assertEqual(report["allowed_tools"], [])

    def test_real_doctor_enables_workspace_tools_but_not_delegation_for_coding(self):
        report = self.report(self.cli_doctor("--profile", "coding"))
        tools = set(report["allowed_tools"])
        self.assertIn("read", tools)
        self.assertTrue(tools & {"edit", "write"}, tools)
        self.assertTrue(tools & {"shell", "bash"}, tools)
        self.assertFalse(
            tools - {"read", "edit", "write", "shell", "bash", "glob", "grep", "patch",
                     "apply_patch", "external_directory", "question", "todo", "todowrite"},
            f"Unexpected effective coding tools: {tools}",
        )
        self.assertNotIn("external_directory", tools, "Workspace tools must not grant external access")

    def test_real_doctor_refuses_instructions_or_custom_agent_in_effective_config(self):
        for label in ("instructions", "agent"):
            with self.subTest(contamination=label):
                diagnostic = self.root / "diagnostic.json"
                diagnostic.unlink(missing_ok=True)
                self.launcher(label)
                result = self.cli_doctor()
                output = result.stdout + result.stderr
                self.assertTrue(diagnostic.exists(), output)
                observed = json.loads(diagnostic.read_text(encoding="utf-8"))
                for operation in ("config.get", "agent.list"):
                    self.assertEqual(observed[operation]["returncode"], 0, observed[operation])
                config = json.loads(observed["config.get"]["stdout"])
                agents = json.loads(observed["agent.list"]["stdout"])
                if label == "instructions":
                    self.assertTrue(any(
                        entry.get("type") == "document"
                        and any(path.endswith("/opencode/AGENTS.md")
                                for path in entry["info"].get("instructions", []))
                        for entry in config
                    ), config)
                else:
                    self.assertIn(AGENT, {agent["id"] for agent in agents["data"]}, agents)
                self.assertNotEqual(result.returncode, 0, output)
                self.assertRegex(output, ISOLATION_ERROR)
                self.assertNotIn(MARKER, output, "A rejection must not quote instruction content")
                self.assertFalse(self.log.exists(), "Contamination must be rejected before inference")

    def test_non_elf_override_requires_safe_fixture_opt_in_before_execution(self):
        wrapper = self.root / "untrusted-wrapper"
        wrapper.write_text(
            "#!/bin/sh\n"
            'printf executed > "$XDG_CONFIG_HOME/wrapper-executed"\n'
            "sleep 1\n"
            "exit 1\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o700)
        self.env["BENCHMARK_OPENCODE_BIN"] = str(wrapper)
        # Observe the private runtime while it exists, before the adapter removes it.
        controller = """
            import json
            import subprocess
            import sys
            import time
            from pathlib import Path

            process = subprocess.Popen(
                [sys.executable, '-B', '-m', 'benchmark', 'doctor',
                 '--model', sys.argv[2], '--json'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            executed = False
            while process.poll() is None:
                executed |= any(Path(sys.argv[1]).rglob('wrapper-executed'))
                time.sleep(0.01)
            stdout, stderr = process.communicate()
            print(json.dumps({'executed': executed, 'returncode': process.returncode,
                              'stdout': stdout, 'stderr': stderr}))
        """
        for label, url, credential in (
            ("normal environment", None, None),
            ("non-loopback fixture", "http://192.0.2.1:18999/v1", None),
            ("fixture with credential", FIXTURE_URL, "test-only-not-a-real-credential"),
        ):
            with self.subTest(environment=label):
                self.env.pop("BENCHMARK_OPENCODE_LOOPBACK_URL", None)
                self.env.pop("OPENCODE_API_KEY", None)
                if url is not None:
                    self.env["BENCHMARK_OPENCODE_LOOPBACK_URL"] = url
                if credential is not None:
                    self.env["OPENCODE_API_KEY"] = credential
                result = self.launch(sys.executable, "-B", "-c", textwrap.dedent(controller),
                                     self.tmp, MODEL)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                observed = json.loads(result.stdout)
                output = observed["stdout"] + observed["stderr"]
                self.assertFalse(observed["executed"], "Non-ELF wrapper ran before rejection")
                self.assertNotEqual(observed["returncode"], 0, output)
                self.assertRegex(output, ISOLATION_ERROR)
                self.assertFalse(self.log.exists(), "Rejection must happen before inference")

    def run_case(self, workspace):
        code = f"""
            import importlib.util
            import json
            from pathlib import Path

            assert importlib.util.find_spec('benchmark.opencode_adapter') is not None, \\
                'OpenCode run_case feature unavailable'
            from benchmark import opencode_adapter

            adapter = getattr(opencode_adapter, 'run_case', None)
            assert callable(adapter), 'OpenCode run_case feature unavailable'
            print(json.dumps(adapter({MODEL!r}, list({TURNS!r}),
                                     Path({str(workspace)!r}), coding=False)))
        """
        return self.launch(sys.executable, "-B", "-c", textwrap.dedent(code))

    def test_case_uses_requested_model_and_continues_same_session_on_follow_up(self):
        workspace = self.root / "case"
        workspace.mkdir()
        result = self.run_case(workspace)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["answers"], list(ANSWERS))
        self.assertIsInstance(report["evidence"], str)
        invocations = [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(invocations), 2)
        first, second = [record["argv"] for record in invocations]
        self.assertIn(MODEL, first)
        self.assertIn(TURNS[0], first)
        self.assertNotIn(TURNS[1], first, "Future turns must not be injected into the first prompt")
        self.assertIn(TURNS[1], second)
        self.assertIn(SESSION, second, "Follow-up must explicitly select the original session")
        self.assertNotIn("--continue", second, "Never resume the ambient last session")
        self.assertEqual([Path(record["cwd"]).resolve() for record in invocations], [workspace] * 2)


if __name__ == "__main__":
    unittest.main()
