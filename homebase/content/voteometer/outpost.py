import subprocess

subprocess.Popen(['flask', '--app', 'voteometer', 'run', '-p', '5002', '--host=0.0.0.0'])