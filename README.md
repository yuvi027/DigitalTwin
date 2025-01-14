# On Demand Slicing
This project implements a network slicing approach in the **ComNetsEmu** platform. It allows users to dynamically activate or deactivate network slices via CLI commands. A single Ryu SDN controller is used to manage the network slices.

---

## **University Campus Network**
![project-diagram_version_2](https://github.com/user-attachments/assets/1cfa6fbe-4ad9-4b53-a04b-e418e9eedb01)

This project simulates a university campus where there are dedicated slices for researchers and students. Researchers have 2 types of traffic, regular communication, and simulation. Meanwhile, students have only communication traffic. There are two slices, shared and researchers slices. Their functiuons depend on the scenario:

1. When there is no exam or simulation, the shared slice is reserved for students, and the researchers slice is reserved for the regular researchers' communication.
2. When there is no exam but a simulation is being run, the shared slice is shared 50/50 between students and researchers' communication, while the researchers' slice is reserved for simulation traffic.
3. When an exam and a simulation are both running, the shared slice is reserved only for researchers communication, and the researchers' slice is reserved for simulation traffic.
4. When there is an exam and no simulation, the shared slice is deactivated, and the researchers' slice is reserved for regular researchers' communication.

The four scenarios are depicted in the matrix:
![matrix_version_4](https://github.com/user-attachments/assets/496e5e34-02e6-435b-952b-74b7d53f1000)

The default setup is in the bottom right in yellow.


## **Installation**

### Prerequisites 

**Install ComNetsEmu**:
   Follow the installation guide for ComNetsEmu from the official repository: [ComNetsEmu GitHub](https://github.com/stevelorenz/comnetsemu).

   It's best to run the program in a Virtual Machine that already has ComNetsEmu installed: [ComNetsEmu VM Image](https://www.granelli-lab.org/researches/relevant-projects/comnetsemu-labs).
   
### Clone the Repository 
Open your terminal and run the following command to clone the repository:

```bash
git clone https://github.com/yuvi027/OnDemandSlicing.git

cd OnDemandSlicing
```

## **Usage**

### Step 1: Start the Ryu Controller

Navigate to the project directory and launch the Ryu controller:

```bash
ryu-manager controller.py
```

### Step 2: Run the Network Topology

In a separate terminal, run the predefined network topology:

```bash
sudo python3 network.py
```

### Step 3: Run the Control Panel

In another terminal, run the control panel (this lets us change the scenarios):

```bash
sudo python3 control_panel.py
```

### Step 4: Test and Monitor Slices

- Use the Mininet CLI to interact with hosts and test network performance. Example commands:

  ```bash
  mininet> pingall  # Test connectivity between hosts
  mininet> xterm R1 R2  # Open terminals for simulation between the researchers
  ```

- If you want to change the scenario, it's possible by giving the control panel the values of the exam (true or false) and simulation (true or false).
---

## **Testing**

1. **Slicing Validation**:
   - Use `iperf` to test bandwidth allocation between hosts. We have defined simulation traffic as TCP traffic between the researchers on port 6000. Testing can be done by iperf and verification using wireshark.
   ```bash
   iperf -s -p 6000           # On one host
   iperf -c <host-ip> -p 6000 # On another host
   ```

2.  **Bandwidth Validation**:

   To verify quality of service in the shared slice, use iperf simultaneously between the researchers and the students (not on port 6000).

---

## **References**

- [ComNetsEmu GitHub](https://github.com/stevelorenz/comnetsemu)
- [Ryu SDN Framework](https://ryu.readthedocs.io/en/latest/)
- [Mininet Documentation](http://mininet.org/walkthrough/)

