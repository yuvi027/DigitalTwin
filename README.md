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

- This project simulate the real world scenario of a unitveristy campus where there are dedicated slices for research labs and students. There are three scenarios that will lead to activation and deactivation of slices:
  1.  If there is an ongoing exam, the student slice will be deactivated in order to prevent student devices communicating
  2.  If there is a simulation being run in the research lab the researcher's packets are prioritized in the network
  3.  Else the network is shared equally

# (Edit this as needed)

## **Installation**

### Prerequisites 

1. **Install ComNetsEmu**:
   Follow the installation guide for ComNetsEmu from the official repository: [ComNetsEmu GitHub](https://github.com/stevelorenz/comnetsemu).

2. **Install Ryu Controller**:
   ```bash
   pip install ryu
   ```

3. **Additional Dependencies**:
   ```bash
   sudo apt-get install python3 python3-pip
   pip install mininet
   ```

### Clone the Repository 
```bash
git clone <repository-url>
cd on-demand-sdn-slices
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
