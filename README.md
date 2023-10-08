# LOG8415

This repository is for Lab 1 assignment about  cluster Benchmarking using EC2 Virtual Machines and Elastic Load Balancer

Presented by :
- Mehdi Belchiti
- Anass EL AZOUZI
- Zakaria Haniri
- Guillaume MARTIN

Our script.sh code is divided into two parts :
- The first part is dedicated to the setup of our architecture (EC2 instances, security group, key pair, target groups, Load balancer, listener and its rules...).
  The flask application deployment is also automatically done while creating EC2 instances with passing the flask deployment script in ‘UserData’ argument.
  NB : We can put this part as a comment if the setup is already created.
  
- The second part is dedicated to creating the Docker image to launch in it the benchmark cluster codes to send the test scenario requests, collect the metrics data from AWS Cloudwatch and present them in plots.

In order to run the script.sh, the user needs to:

- Fill in the lines ( aws_access_key_id,aws_secret_access_key,aws_session_token) in the script.sh file with his credentials.
- Have already installed python on his PC.
- Have already installed Docker in his PC.
