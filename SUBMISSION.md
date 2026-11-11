# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `cloud-init.yaml`: what the VM installs and starts on first boot
- [ ] `notes.md` with your `az` commands (optional)

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste the `az` commands you used to create the network, the NSG, the public IP and the VM. Map each to its AWS equivalent (VPC, security group, Elastic IP, EC2): which is the same idea, and which is different in Azure?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Paste your NSG rules with their priorities. How does Azure choose between two rules that both match? What are the three default inbound rules that you did not write, and why does the lowest-numbered rule win?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. Why is the SSH rule limited to one /32 and why is `password authentication` off? What happens to your access when your IP changes?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Paste the relevant lines of `cloud-init.yaml` and the output of `az vm run-command invoke` for `systemctl status beanie@gateway`. What runs the services at boot, and what restarts one that crashes?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. Ports 8001 to 8004 are open on the VM itself but closed to the internet. Which layer closes them, and what would you change to open the gateway only to a load balancer?

**Your answer:**

<!-- replace this line with your answer -->

### Q6. What does it cost to leave this VM running for a month? Name two things in the resource group that bill even when the VM is stopped (deallocated vs stopped).

**Your answer:**

<!-- replace this line with your answer -->

### Q7. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q8. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
