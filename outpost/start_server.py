import subprocess

def start_server(outpost_def):
    print("starting server")
    subprocess.Popen(['flask', '--app', 'receiver', 'run', '-p', '5001', '--host=0.0.0.0'])
