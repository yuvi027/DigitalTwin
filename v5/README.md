# On Demand Slicing
This project implements a network slicing approach in the **ComNetsEmu** platform. It allows users to dynamically activate or deactivate network slices via CLI/GUI commands. A single SDN controller, such as Ryu, is used to manage the network slices.

---

## **Features**

- **Dynamic Slicing**: Activate and deactivate slices based on user requirements.
- **Customizable Topology**: Define network topologies directly in Python.
- **Flexible Slice Configuration**: Allocate bandwidth, define flows, and set priorities for each slice.
- **Real-Time Traffic Management**: Adjust network parameters dynamically to suit real-world demands.

---

## **University Campus Network**
![project-diagram_version_2](https://github.com/user-attachments/assets/1cfa6fbe-4ad9-4b53-a04b-e418e9eedb01)

This project simulate the real world scenario of a unitveristy campus where there are dedicated slices for researchers and students exams. We have 2 slices:

1. Shared slice: When there is no exam or simulation, the link is for students. When there is no exam and a simulation is being run, it is shared 50/50 between students and simulation traffic. When there is an exam and a simulation, the link is for simulation. When there is an exam and no simulation, the link is deactivated.
2. Researcher slice: Only for normal researcher traffic. Always active by default

There are four scenarios:
![matrix_version_3](https://github.com/user-attachments/assets/c5f595e7-a4b1-48fd-a2fe-55a182a0969a)

The default setup for the network is that exam = false and simulation = false. Hence the student slice is only used by students and the research slice is only used for normal researcher traffic. 


## **Installation**

### Clone the Repository 
Open your terminal and run the following command to clone the repository:

```bash
git clone https://github.com/yuvi027/OnDemandSlicing.git
cd OnDemandSlicing
```
### Prerequisites 

1. **Install ComNetsEmu**:
   Follow the installation guide for ComNetsEmu from the official repository: [ComNetsEmu GitHub](https://github.com/stevelorenz/comnetsemu).
   
1. **Install Git Dependencies**:
```bash
pip install -r requirements.txt (NEED TO CREATE -> include ryu, python3 python3-pip, mininet)
```
---
# SHOULD BE IN THE REQUIREMENT
**Install Ryu Controller**:
   ```bash
   pip install ryu
   ```
**Additional Dependencies**:
   ```bash
   sudo apt-get install python3 python3-pip
   pip install mininet
   ```
---

## **Usage**

### Step 1: Define the Topology
Define your network topology in the Python file (e.g., `custom_topology.py`). Example:

```python
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.topo import Topo

class CustomTopology(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links with bandwidth constraints
        self.addLink(h1, s1, bw=10)
        self.addLink(h2, s1, bw=10)
        self.addLink(s1, s2, bw=20)
        self.addLink(s2, h3, bw=10)
        self.addLink(s2, h4, bw=10)

if __name__ == "__main__":
    net = Mininet(topo=CustomTopology(), controller=RemoteController, link=TCLink)
    net.start()
    net.pingAll()
    net.stop()
```

### Step 2: Configure the Controller
Use the `Ryu` controller to define flow rules for each slice. Example:

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet, ethernet, ipv4, tcp
from ryu.ofproto import ofproto_v1_3

class SliceController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SliceController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # Define flow rules here
        self.logger.info("Switch connected: %s", ev.msg.datapath.id)
```

### Step 3: Launch the Topology
1. Start the Ryu controller:
   ```bash
   ryu-manager slice_controller.py
   ```
2. Run the Mininet topology:
   ```bash
   sudo python3 custom_topology.py
   ```

### Step 4: Activate Slices
Use CLI commands to dynamically activate or deactivate slices:
- Example:
   ```bash
   mininet> xterm h1 h3
   ```
   - Send traffic between `h1` and `h3` to test slice performance.

---

## **Testing**

1. **Bandwidth Validation**:
   - Use `iperf` to test bandwidth allocation between hosts.
   ```bash
   iperf -s  # On one host
   iperf -c <host-ip>  # On another host
   ```

2. **Latency Measurement**:
   - Use `ping` to measure latency.
   ```bash
   ping <host-ip>
   ```

3. **Dynamic Adjustments**:
   - Modify slice configurations and observe real-time changes in performance.

---

## **Customization**

- **Topologies**: Edit the `custom_topology.py` file to create your own network setups.
- **Slices**: Update the controller logic in `slice_controller.py` to define new slice types.
- **Traffic Patterns**: Use traffic generators like `iperf` or `ping` to simulate specific traffic patterns.

---

## **Future Work**

- Integrate a GUI for slice activation/deactivation.
- Add support for multi-controller setups.
- Test with more complex topologies and traffic scenarios.

---

## **References**

- [ComNetsEmu GitHub](https://github.com/stevelorenz/comnetsemu)
- [Ryu SDN Framework](https://ryu.readthedocs.io/en/latest/)
- [Mininet Documentation](http://mininet.org/walkthrough/)
