import subprocess
import tempfile
import os
import signal
from typing import Dict, Optional


class CompilerService:
    """Service for safely compiling and running C code"""

    def __init__(self, timeout: int = 3, max_memory_mb: int = 50):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb

    def compile_and_run(self, code: str, input_data: str = "") -> Dict:
        """
        Safely compile and run C code with resource limits

        Args:
            code: C source code to compile and run
            input_data: Optional stdin input for the program

        Returns:
            Dictionary with compilation/execution results
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = os.path.join(tmpdir, 'code.c')
            exec_file = os.path.join(tmpdir, 'program')

            # Write code to file
            try:
                with open(code_file, 'w') as f:
                    f.write(code)
            except Exception as e:
                return {
                    'success': False,
                    'stage': 'write',
                    'error': f'Failed to write code: {str(e)}'
                }

            # Compile the code
            compile_result = self._compile(code_file, exec_file)
            if not compile_result['success']:
                return compile_result

            # Run the compiled program
            return self._run(exec_file, input_data)

    def _compile(self, code_file: str, exec_file: str) -> Dict:
        """Compile C code with gcc"""
        try:
            result = subprocess.run(
                ['gcc', '-Wall', '-Wextra', '-std=c11', '-o', exec_file, code_file],
                capture_output=True,
                timeout=self.timeout,
                text=True
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'stage': 'compilation',
                    'error': result.stderr,
                    'warnings': result.stdout
                }

            return {
                'success': True,
                'warnings': result.stderr  # gcc warnings go to stderr
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stage': 'compilation',
                'error': 'Compilation timeout (code too complex)'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'stage': 'compilation',
                'error': 'gcc compiler not found. Please install gcc.'
            }
        except Exception as e:
            return {
                'success': False,
                'stage': 'compilation',
                'error': f'Compilation error: {str(e)}'
            }

    def _run(self, exec_file: str, input_data: str = "") -> Dict:
        """Run compiled program with resource limits"""
        try:
            # Set resource limits (Unix-like systems)
            def set_limits():
                # Memory limit (in bytes)
                try:
                    import resource
                    max_memory = self.max_memory_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
                except:
                    pass  # Resource limits not available on all systems

            result = subprocess.run(
                [exec_file],
                input=input_data,
                capture_output=True,
                timeout=self.timeout,
                text=True,
                preexec_fn=set_limits if os.name != 'nt' else None  # Unix only
            )

            return {
                'success': True,
                'stage': 'execution',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stage': 'execution',
                'error': f'Program timeout (exceeded {self.timeout} seconds)',
                'stdout': '',
                'stderr': ''
            }
        except Exception as e:
            return {
                'success': False,
                'stage': 'execution',
                'error': f'Runtime error: {str(e)}',
                'stdout': '',
                'stderr': ''
            }

    def validate_syntax(self, code: str) -> Dict:
        """Quick syntax validation without running"""
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = os.path.join(tmpdir, 'code.c')

            try:
                with open(code_file, 'w') as f:
                    f.write(code)

                # Syntax check only
                result = subprocess.run(
                    ['gcc', '-fsyntax-only', '-Wall', '-Wextra', code_file],
                    capture_output=True,
                    timeout=2,
                    text=True
                )

                return {
                    'valid': result.returncode == 0,
                    'errors': result.stderr if result.returncode != 0 else None,
                    'warnings': result.stderr if result.returncode == 0 else None
                }

            except Exception as e:
                return {
                    'valid': False,
                    'errors': str(e)
                }
