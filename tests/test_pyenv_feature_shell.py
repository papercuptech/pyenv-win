import subprocess
from pathlib import Path
from tempenv import TemporaryEnvironment
from test_pyenv import TestPyenvBase
from test_pyenv_helpers import not_installed_output, run_pyenv_test


class TestPyenvFeatureShell(TestPyenvBase):
    def test_no_shell_version(self, setup):
        def commands(ctx):
            assert ctx.pyenv("shell") == "no shell-specific version configured"
        with TemporaryEnvironment({"PYENV_VERSION": ""}):
            run_pyenv_test({}, commands)

    def test_shell_version_defined(self, setup):
        def commands(ctx):
            assert ctx.pyenv("shell") == "3.9.2"
        with TemporaryEnvironment({"PYENV_VERSION": "3.9.2"}):
            run_pyenv_test({}, commands)

    def test_shell_set_installed_version(self, setup):
        def commands(ctx):
            pyenv_bat = Path(ctx.pyenv_path, r'bin\pyenv.bat')
            tmp_bat = str(Path(ctx.local_path, "tmp.bat"))
            with open(tmp_bat, "w") as f:
                # must chain commands because env var is lost when cmd ends
                print(f'@call {pyenv_bat} shell 3.7.7 & call {pyenv_bat} shell', file=f)
            args = ['cmd', '/d', '/c', 'call', tmp_bat]
            result = subprocess.run(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = str(result.stdout, "utf-8").strip()
            assert output == "3.7.7"

        with TemporaryEnvironment({"PYENV_VERSION": "3.8.9"}):
            run_pyenv_test({'versions': ["3.7.7", "3.8.9"]}, commands)

    def test_shell_set_unknown_version(self, setup):
        def commands(ctx):
            assert ctx.pyenv(["shell", "3.7.8"]) == not_installed_output("3.7.8")
        run_pyenv_test({'versions': ["3.8.9"]}, commands)
