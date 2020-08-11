import subprocess


def run():
    output = subprocess.Popen("aws inspector start-assessment-run --assessment-template-arn arn:aws:inspector:us-east-1:396964816994:target/0-NdN74TQ6/template/0-mwgfjdcZ", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return((output.stdout.read()).decode("utf-8"))

f = open("/home/ubuntu/Inspector/arn.txt", "w")
run_arn = run()
f.write(run_arn)
f.close()
print("run started")
